import json
import uuid
import requests
import urllib.request
import urllib.error
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sslcommerz_lib import SSLCOMMERZ

from .models import Order, Product, CartItem, Category
from .serializers import (
    UserRegistrationSerializer,
    ProductSerializer,
    CartItemSerializer,
    OrderSerializer,
    CategorySerializer,
)
from .notifications import send_order_notifications


# ─────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class   = UserRegistrationSerializer


# ─────────────────────────────────────────────────────────────────────
# Products & Categories
# ─────────────────────────────────────────────────────────────────────

class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class   = ProductSerializer
    queryset           = Product.objects.all().order_by('-id')
    search_fields      = ['name', 'description']
    filterset_fields   = ['category']
    ordering_fields    = ['price', 'created_at']


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class   = CategorySerializer
    queryset           = Category.objects.all()


# ─────────────────────────────────────────────────────────────────────
# Cart
# ─────────────────────────────────────────────────────────────────────

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user)
        return Response(CartItemSerializer(items, many=True).data)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity   = int(request.data.get('quantity', 1))
        product    = get_object_or_404(Product, id=product_id)

        item, created = CartItem.objects.get_or_create(
            user=request.user, product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        item_id = request.data.get('item_id')
        CartItem.objects.filter(id=item_id, user=request.user).delete()
        return Response({'message': 'Removed'})


# ─────────────────────────────────────────────────────────────────────
# Orders (list existing orders)
# ─────────────────────────────────────────────────────────────────────

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return Response(OrderSerializer(orders, many=True).data)


# ─────────────────────────────────────────────────────────────────────
# Stripe (placeholder — keys not configured)
# ─────────────────────────────────────────────────────────────────────

class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'error': 'Stripe not configured'}, status=400)


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({'status': 'ok'})


# ─────────────────────────────────────────────────────────────────────
# SSLCommerz (legacy — keeping for backward compatibility)
# ─────────────────────────────────────────────────────────────────────

class SSLCommerzInitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'error': 'Use /api/orders/create/ instead'}, status=400)


class SSLCommerzSuccessView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        tran_id = request.data.get('tran_id', '')
        orders  = Order.objects.filter(transaction_id=tran_id)
        orders.update(payment_status='paid', order_status='confirmed')
        for order in orders:
            send_order_notifications(order)
        return redirect(f"{settings.FRONTEND_URL}/?payment=success")


class SSLCommerzFailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        tran_id = request.data.get('tran_id', '')
        Order.objects.filter(transaction_id=tran_id).update(payment_status='failed')
        return redirect(f"{settings.FRONTEND_URL}/?payment=failed")


class SSLCommerzCancelView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return redirect(f"{settings.FRONTEND_URL}/?payment=cancelled")


# ─────────────────────────────────────────────────────────────────────
# AI Admin Assistant
# ─────────────────────────────────────────────────────────────────────

@staff_member_required
@require_POST
@csrf_exempt
def ai_product_suggest(request):
    try:
        body   = json.loads(request.body)
        prompt = body.get("prompt", "").strip()
        if not prompt:
            return JsonResponse({"error": "prompt is required"}, status=400)
        api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        if not api_key:
            return JsonResponse({"error": "ANTHROPIC_API_KEY not configured"}, status=500)
        payload = json.dumps({
            "model":      "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages":   [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type":      "application/json",
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data  = json.loads(resp.read())
            reply = next(
                (b["text"] for b in data.get("content", []) if b.get("type") == "text"),
                "No response.",
            )
            return JsonResponse({"reply": reply})
    except urllib.error.HTTPError as e:
        return JsonResponse({"error": f"Anthropic API error: {e.code}"}, status=502)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ─────────────────────────────────────────────────────────────────────
# Order Create — payment সহ (নতুন)
# ─────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    d       = request.data
    product = get_object_or_404(Product, id=d.get('product_id'))
    qty     = int(d.get('quantity', 1))
    method  = d.get('payment_method', 'cod')

    product_total_bdt = Decimal(str(product.price)) * qty * Decimal('110')
    delivery_charge   = Decimal(str(d.get('delivery_charge', 80)))
    grand_total_bdt   = product_total_bdt + delivery_charge
    tran_id           = f"SHOPBD-{uuid.uuid4().hex[:14].upper()}"

    order = Order.objects.create(
        user            = request.user if request.user.is_authenticated else None,
        product         = product,
        quantity        = qty,
        address         = d.get('address', ''),
        phone           = d.get('phone', ''),
        delivery_zone   = d.get('delivery_zone', 'inside'),
        delivery_charge = delivery_charge,
        payment_method  = method,
        payment_status  = 'pending',
        total_amount    = grand_total_bdt,
        transaction_id  = tran_id,
    )

    # COD
    if method == 'cod':
        order.order_status = 'confirmed'
        order.save()
        send_order_notifications(order)
        return Response({'id': order.id, 'payment_url': None})

    # bKash
    if method == 'bkash':
        try:
            token_res = requests.post(
                'https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/token/grant',
                json={'app_key': settings.BKASH_APP_KEY, 'app_secret': settings.BKASH_APP_SECRET},
                headers={'username': settings.BKASH_USERNAME, 'password': settings.BKASH_PASSWORD},
                timeout=15,
            ).json()
            id_token = token_res.get('id_token')
            if not id_token:
                return Response({'error': 'bKash token পাওয়া যায়নি'}, status=400)
            pay_res = requests.post(
                'https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/create',
                json={
                    'mode': '0011', 'payerReference': str(order.id),
                    'callbackURL': f"{settings.BASE_URL}/api/payment/bkash/callback/",
                    'amount': str(grand_total_bdt), 'currency': 'BDT',
                    'intent': 'sale', 'merchantInvoiceNumber': tran_id,
                },
                headers={'Authorization': id_token, 'X-APP-Key': settings.BKASH_APP_KEY},
                timeout=15,
            ).json()
            url = pay_res.get('bkashURL')
            if not url:
                return Response({'error': 'bKash URL পাওয়া যায়নি', 'detail': pay_res}, status=400)
            return Response({'id': order.id, 'payment_url': url})
        except requests.RequestException as e:
            return Response({'error': f'bKash error: {str(e)}'}, status=502)

    # SSL Commerz
    if method == 'ssl':
        try:
            sslcz = SSLCOMMERZ({
                'store_id':   settings.SSL_STORE_ID,
                'store_pass': settings.SSL_STORE_PASS,
                'issandbox':  False,
            })
            res = sslcz.createSession({
                'total_amount': float(grand_total_bdt), 'currency': 'BDT', 'tran_id': tran_id,
                'success_url': f"{settings.BASE_URL}/api/payment/ssl/success/",
                'fail_url':    f"{settings.BASE_URL}/api/payment/ssl/fail/",
                'cancel_url':  f"{settings.BASE_URL}/api/payment/ssl/cancel/",
                'cus_name':    getattr(request.user, 'username', 'Customer'),
                'cus_email':   getattr(request.user, 'email', 'customer@shopbd.com'),
                'cus_phone':   d.get('phone', ''), 'cus_add1': d.get('address', ''),
                'cus_country': 'Bangladesh', 'shipping_method': 'NO',
                'product_name': product.name, 'product_category': 'General', 'product_profile': 'general',
            })
            if res.get('status') != 'SUCCESS':
                return Response({'error': 'SSL Commerz session তৈরি হয়নি'}, status=400)
            return Response({'id': order.id, 'payment_url': res['GatewayPageURL']})
        except Exception as e:
            return Response({'error': f'SSL Commerz error: {str(e)}'}, status=502)

    # Shurjopay
    if method == 'shurjopay':
        try:
            auth = requests.post(
                'https://engine.shurjopayment.com/api/get_token',
                json={'username': settings.SHURJOPAY_USERNAME, 'password': settings.SHURJOPAY_PASSWORD},
                timeout=15,
            ).json()
            token = auth.get('token')
            store_id = auth.get('store_id')
            if not token:
                return Response({'error': 'Shurjopay token পাওয়া যায়নি'}, status=400)
            pay = requests.post(
                'https://engine.shurjopayment.com/api/secret-pay',
                json={
                    'prefix': 'SP', 'token': token, 'store_id': store_id,
                    'return_url': f"{settings.BASE_URL}/api/payment/shurjopay/callback/",
                    'cancel_url': f"{settings.BASE_URL}/api/payment/shurjopay/cancel/",
                    'amount': float(grand_total_bdt), 'currency': 'BDT', 'order_id': tran_id,
                    'discsount_amount': 0, 'disc_percent': 0,
                    'customer_name':    getattr(request.user, 'username', 'Customer'),
                    'customer_email':   getattr(request.user, 'email', 'customer@shopbd.com'),
                    'customer_phone':   d.get('phone', ''), 'customer_address': d.get('address', ''),
                    'customer_city': 'Dhaka', 'customer_postcode': '1200',
                    'customer_country': 'Bangladesh', 'value1': str(order.id),
                },
                timeout=15,
            ).json()
            url = pay.get('checkout_url')
            if not url:
                return Response({'error': 'Shurjopay URL পাওয়া যায়নি', 'detail': pay}, status=400)
            return Response({'id': order.id, 'payment_url': url})
        except requests.RequestException as e:
            return Response({'error': f'Shurjopay error: {str(e)}'}, status=502)

    return Response({'error': 'Invalid payment method'}, status=400)


# ─────────────────────────────────────────────────────────────────────
# Payment Callbacks
# ─────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def bkash_callback(request):
    status  = request.GET.get('status', '')
    tran_id = request.data.get('merchantInvoiceNumber', request.GET.get('paymentID', ''))
    if status == 'success':
        orders = Order.objects.filter(transaction_id__icontains=tran_id)
        orders.update(payment_status='paid', order_status='confirmed')
        for order in orders:
            send_order_notifications(order)
        return redirect(f"{settings.FRONTEND_URL}/?payment=success")
    Order.objects.filter(transaction_id__icontains=tran_id).update(payment_status='failed')
    return redirect(f"{settings.FRONTEND_URL}/?payment=failed")


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def ssl_success(request):
    tran_id = request.data.get('tran_id', '')
    orders  = Order.objects.filter(transaction_id=tran_id)
    orders.update(payment_status='paid', order_status='confirmed')
    for order in orders:
        send_order_notifications(order)
    return redirect(f"{settings.FRONTEND_URL}/?payment=success")


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def ssl_fail(request):
    Order.objects.filter(transaction_id=request.data.get('tran_id', '')).update(payment_status='failed')
    return redirect(f"{settings.FRONTEND_URL}/?payment=failed")


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def ssl_cancel(request):
    return redirect(f"{settings.FRONTEND_URL}/?payment=cancelled")


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def shurjopay_callback(request):
    order_id = request.GET.get('order_id', request.data.get('order_id', ''))
    orders   = Order.objects.filter(transaction_id=order_id)
    orders.update(payment_status='paid', order_status='confirmed')
    for order in orders:
        send_order_notifications(order)
    return redirect(f"{settings.FRONTEND_URL}/?payment=success")


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def shurjopay_cancel(request):
    return redirect(f"{settings.FRONTEND_URL}/?payment=cancelled")
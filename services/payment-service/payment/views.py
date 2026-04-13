import uuid
import requests
from decimal import Decimal

from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from sslcommerz_lib import SSLCOMMERZ
from .models import Payment


def update_order_payment(order_id, payment_status, order_status):
    """order-service কে payment status জানানো"""
    try:
        requests.patch(
            f"{settings.ORDER_SERVICE_URL}/api/orders/{order_id}/",
            json={'payment_status': payment_status, 'order_status': order_status},
            timeout=5,
        )
    except requests.RequestException:
        pass


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_payment(request):
    d              = request.data
    order_id       = d.get('order_id')
    amount         = Decimal(str(d.get('amount', 0)))
    method         = d.get('payment_method', 'cod')
    phone          = d.get('phone', '')
    address        = d.get('address', '')
    product_name   = d.get('product_name', 'Product')
    user_id        = d.get('user_id')
    tran_id        = f"SHOPBD-{uuid.uuid4().hex[:14].upper()}"

    payment = Payment.objects.create(
        order_id       = order_id,
        user_id        = user_id,
        transaction_id = tran_id,
        payment_method = method,
        amount         = amount,
    )

    # ── COD ──────────────────────────────────────────
    if method == 'cod':
        payment.payment_status = 'paid'
        payment.save()
        update_order_payment(order_id, 'paid', 'confirmed')
        return Response({'id': payment.id, 'payment_url': None, 'transaction_id': tran_id})

    # ── bKash ─────────────────────────────────────────
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
                    'mode': '0011', 'payerReference': str(order_id),
                    'callbackURL': f"{settings.BASE_URL}/api/payment/bkash/callback/",
                    'amount': str(amount), 'currency': 'BDT',
                    'intent': 'sale', 'merchantInvoiceNumber': tran_id,
                },
                headers={'Authorization': id_token, 'X-APP-Key': settings.BKASH_APP_KEY},
                timeout=15,
            ).json()
            url = pay_res.get('bkashURL')
            if not url:
                return Response({'error': 'bKash URL পাওয়া যায়নি'}, status=400)
            payment.payment_url = url
            payment.save()
            return Response({'id': payment.id, 'payment_url': url, 'transaction_id': tran_id})
        except requests.RequestException as e:
            return Response({'error': f'bKash error: {str(e)}'}, status=502)

    # ── SSL Commerz ───────────────────────────────────
    if method == 'ssl':
        try:
            sslcz = SSLCOMMERZ({
                'store_id':   settings.SSL_STORE_ID,
                'store_pass': settings.SSL_STORE_PASS,
                'issandbox':  False,
            })
            res = sslcz.createSession({
                'total_amount': float(amount), 'currency': 'BDT', 'tran_id': tran_id,
                'success_url': f"{settings.BASE_URL}/api/payment/ssl/success/",
                'fail_url':    f"{settings.BASE_URL}/api/payment/ssl/fail/",
                'cancel_url':  f"{settings.BASE_URL}/api/payment/ssl/cancel/",
                'cus_name':    'Customer', 'cus_email': 'customer@shopbd.com',
                'cus_phone':   phone, 'cus_add1': address,
                'cus_country': 'Bangladesh', 'shipping_method': 'NO',
                'product_name': product_name, 'product_category': 'General',
                'product_profile': 'general',
            })
            if res.get('status') != 'SUCCESS':
                return Response({'error': 'SSL session তৈরি হয়নি'}, status=400)
            url = res['GatewayPageURL']
            payment.payment_url = url
            payment.save()
            return Response({'id': payment.id, 'payment_url': url, 'transaction_id': tran_id})
        except Exception as e:
            return Response({'error': f'SSL error: {str(e)}'}, status=502)

    # ── Shurjopay ─────────────────────────────────────
    if method == 'shurjopay':
        try:
            auth = requests.post(
                'https://engine.shurjopayment.com/api/get_token',
                json={'username': settings.SHURJOPAY_USERNAME, 'password': settings.SHURJOPAY_PASSWORD},
                timeout=15,
            ).json()
            token    = auth.get('token')
            store_id = auth.get('store_id')
            if not token:
                return Response({'error': 'Shurjopay token পাওয়া যায়নি'}, status=400)
            pay = requests.post(
                'https://engine.shurjopayment.com/api/secret-pay',
                json={
                    'prefix': 'SP', 'token': token, 'store_id': store_id,
                    'return_url': f"{settings.BASE_URL}/api/payment/shurjopay/callback/",
                    'cancel_url': f"{settings.BASE_URL}/api/payment/shurjopay/cancel/",
                    'amount': float(amount), 'currency': 'BDT', 'order_id': tran_id,
                    'discsount_amount': 0, 'disc_percent': 0,
                    'customer_name': 'Customer', 'customer_email': 'customer@shopbd.com',
                    'customer_phone': phone, 'customer_address': address,
                    'customer_city': 'Dhaka', 'customer_postcode': '1200',
                    'customer_country': 'Bangladesh', 'value1': str(order_id),
                },
                timeout=15,
            ).json()
            url = pay.get('checkout_url')
            if not url:
                return Response({'error': 'Shurjopay URL পাওয়া যায়নি'}, status=400)
            payment.payment_url = url
            payment.save()
            return Response({'id': payment.id, 'payment_url': url, 'transaction_id': tran_id})
        except requests.RequestException as e:
            return Response({'error': f'Shurjopay error: {str(e)}'}, status=502)

    return Response({'error': 'Invalid payment method'}, status=400)


# ── Callbacks ─────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def bkash_callback(request):
    pay_status = request.GET.get('status', '')
    tran_id    = request.data.get('merchantInvoiceNumber', request.GET.get('paymentID', ''))
    payments   = Payment.objects.filter(transaction_id__icontains=tran_id)
    if pay_status == 'success':
        payments.update(payment_status='paid')
        for p in payments:
            update_order_payment(p.order_id, 'paid', 'confirmed')
        return redirect(f"{settings.FRONTEND_URL}/?payment=success")
    payments.update(payment_status='failed')
    return redirect(f"{settings.FRONTEND_URL}/?payment=failed")


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def ssl_success(request):
    tran_id  = request.data.get('tran_id', '')
    payments = Payment.objects.filter(transaction_id=tran_id)
    payments.update(payment_status='paid')
    for p in payments:
        update_order_payment(p.order_id, 'paid', 'confirmed')
    return redirect(f"{settings.FRONTEND_URL}/?payment=success")


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def ssl_fail(request):
    Payment.objects.filter(transaction_id=request.data.get('tran_id', '')).update(payment_status='failed')
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
    payments = Payment.objects.filter(transaction_id=order_id)
    payments.update(payment_status='paid')
    for p in payments:
        update_order_payment(p.order_id, 'paid', 'confirmed')
    return redirect(f"{settings.FRONTEND_URL}/?payment=success")


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def shurjopay_cancel(request):
    return redirect(f"{settings.FRONTEND_URL}/?payment=cancelled")

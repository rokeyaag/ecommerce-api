from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListCreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer, UserRegistrationSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            "message": "তোমার cart",
            "user": request.user.username,
            "items": [
                {"product": "শার্ট", "price": 500},
                {"product": "প্যান্ট", "price": 800},
            ]
        }
        return Response(data)


class ProductView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['stock']
    search_fields = ['name']
    ordering_fields = ['price', 'created_at']

    def perform_create(self, serializer):
        serializer.save()

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 1))
            product = Product.objects.get(id=product_id)
            if product.stock < quantity:
                return Response({"error": "stock নেই!"}, status=400)
            total_price = product.price * quantity
            order = Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=total_price
            )
            product.stock -= quantity
            product.save()
            serializer = OrderSerializer(order)
            return Response({
                "message": "Order হয়ে গেছে!",
                "data": serializer.data
            })
        except Product.DoesNotExist:
            return Response({"error": "Product পাওয়া যায়নি!"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Account তৈরি হয়েছে!",
                "username": user.username,
                "email": user.email,
            })
        return Response(serializer.errors, status=400)
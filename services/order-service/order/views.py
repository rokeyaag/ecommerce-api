import requests, os
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CartItem, Order
from .serializers import CartItemSerializer, OrderSerializer

PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8000')

def get_product_info(product_id):
    try:
        res = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}/", timeout=5)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return None

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    def get_queryset(self): return CartItem.objects.filter(user_id=self.request.user.id)
    def perform_create(self, serializer): serializer.save(user_id=self.request.user.id)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    def get_queryset(self):
        if self.request.user.is_staff: return Order.objects.all()
        return Order.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        product = get_product_info(request.data.get('product_id'))
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        quantity = int(request.data.get('quantity', 1))
        delivery_charge = 80 if request.data.get('delivery_zone') == 'inside' else 120
        total = (float(product['price']) * quantity) + delivery_charge
        serializer = self.get_serializer(data={**request.data, 'user_id': request.user.id,
            'product_name': product['name'], 'product_price': product['price'],
            'total_amount': total, 'delivery_charge': delivery_charge})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

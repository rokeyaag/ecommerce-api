from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, CartItem, Category


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image    = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'image', 'description', 'category', 'created_at']

    def get_image(self, obj):
        if not obj.image:
            return None

        raw = str(obj.image)  # e.g. "https%3A/img.drz.lazcdn.com/..."

        # ── Case 1: already a proper URL stored in the field ──────────────────
        if raw.startswith('http://') or raw.startswith('https://'):
            return raw

        # ── Case 2: URL-encoded external URL (https%3A/... or https%3A%2F%2F...)
        import urllib.parse
        try:
            decoded = urllib.parse.unquote(raw)
            if decoded.startswith('http://') or decoded.startswith('https://'):
                return decoded
        except Exception:
            pass

        # ── Case 3: single-slash encoded (https:/img... → https://img...)
        if raw.startswith('https:/') and not raw.startswith('https://'):
            return 'https://' + raw[7:]
        if raw.startswith('http:/') and not raw.startswith('http://'):
            return 'http://' + raw[6:]

        # ── Case 4: normal local media file → build absolute URL ─────────────
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)

        # fallback
        return obj.image.url


class CartItemSerializer(serializers.ModelSerializer):
    product    = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total      = serializers.SerializerMethodField()

    class Meta:
        model  = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total']

    def get_total(self, obj):
        return float(obj.product.price) * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    product  = ProductSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'product', 'quantity',
            'address', 'phone', 'order_status',
            'payment_method', 'payment_status',
            'transaction_id', 'username', 'created_at',
        ]
        read_only_fields = ['order_status', 'payment_status', 'transaction_id']
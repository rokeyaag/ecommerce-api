from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, CartItem, Category


class UserRegistrationSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("এই email দিয়ে আগেই account আছে।")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password দুটো মিলছে না।"})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category    = CategorySerializer(read_only=True)
    image       = serializers.SerializerMethodField()
    final_image = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'price', 'stock',
            'image', 'image_url', 'final_image',
            'description', 'category', 'created_at',
        ]

    def get_image(self, obj):
        if not obj.image:
            return None

        raw = str(obj.image)

        if raw.startswith('http://') or raw.startswith('https://'):
            return raw

        import urllib.parse
        try:
            decoded = urllib.parse.unquote(raw)
            if decoded.startswith('http://') or decoded.startswith('https://'):
                return decoded
        except Exception:
            pass

        if raw.startswith('https:/') and not raw.startswith('https://'):
            return 'https://' + raw[7:]
        if raw.startswith('http:/') and not raw.startswith('http://'):
            return 'http://' + raw[6:]

        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url

    def get_final_image(self, obj):
        # image_url থাকলে সেটা আগে return করো
        if obj.image_url:
            return obj.image_url
        # না থাকলে image field থেকে নাও
        return self.get_image(obj)


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
            'transaction_id', 'total_amount',
            'username', 'created_at',
        ]
        read_only_fields = ['order_status', 'payment_status', 'transaction_id']
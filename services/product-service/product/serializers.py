from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_final_image(self, obj):
        return obj.get_image()

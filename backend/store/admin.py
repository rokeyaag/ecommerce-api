from django.contrib import admin
from .models import Product, Order, Category, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'price', 'stock', 'category', 'created_at']
    list_editable = ['category']
    list_filter   = ['category']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'product', 'phone', 'payment_method', 'order_status', 'total_amount', 'created_at']
    list_filter   = ['order_status', 'payment_method']
    search_fields = ['phone', 'product__name']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity']
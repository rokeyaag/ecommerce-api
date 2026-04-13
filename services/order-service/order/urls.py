from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet, OrderViewSet

router = DefaultRouter()
router.register('cart', CartItemViewSet, basename='cart')
router.register('', OrderViewSet, basename='order')
urlpatterns = [path('', include(router.urls))]

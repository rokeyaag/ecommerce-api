from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    # Auth
    RegisterView,
    # Products & Categories
    ProductListView, CategoryListView,
    # Cart
    CartView,
    # Orders
    OrderView, create_order,
    # Stripe
    StripeCheckoutView, StripeWebhookView,
    # SSLCommerz (legacy)
    SSLCommerzInitView, SSLCommerzSuccessView, SSLCommerzFailView, SSLCommerzCancelView,
)

urlpatterns = [
    # ✅ Auth
    path('auth/register/',      RegisterView.as_view(),        name='register'),
    path('auth/token/',         TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # Products & Categories
    path('products/',   ProductListView.as_view(),  name='products'),
    path('categories/', CategoryListView.as_view(), name='categories'),

    # Cart
    path('cart/', CartView.as_view(), name='cart'),

    # Orders
    path('orders/',        OrderView.as_view(), name='orders'),
    path('orders/create/', create_order,        name='create_order'),

    # Stripe
    path('stripe/checkout/', StripeCheckoutView.as_view(), name='stripe_checkout'),
    path('stripe/webhook/',  StripeWebhookView.as_view(),  name='stripe_webhook'),

    # SSLCommerz (legacy)
    path('sslcommerz/init/',    SSLCommerzInitView.as_view(),    name='sslcommerz_init'),
    path('sslcommerz/success/', SSLCommerzSuccessView.as_view(), name='sslcommerz_success'),
    path('sslcommerz/fail/',    SSLCommerzFailView.as_view(),    name='sslcommerz_fail'),
    path('sslcommerz/cancel/',  SSLCommerzCancelView.as_view(),  name='sslcommerz_cancel'),
]
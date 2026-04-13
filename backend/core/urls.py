from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.views import (
    ai_product_suggest,
    bkash_callback,
    ssl_success, ssl_fail, ssl_cancel,
    shurjopay_callback, shurjopay_cancel,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # সব store routes (products, orders, auth, cart...)
    path('api/', include('store.urls')),

    # AI Admin Assistant
    path('api/ai-suggest/', ai_product_suggest, name='ai_product_suggest'),

    # bKash callback
    path('api/payment/bkash/callback/', bkash_callback, name='bkash_callback'),

    # SSL Commerz callbacks
    path('api/payment/ssl/success/', ssl_success, name='ssl_success'),
    path('api/payment/ssl/fail/',    ssl_fail,    name='ssl_fail'),
    path('api/payment/ssl/cancel/',  ssl_cancel,  name='ssl_cancel'),

    # Shurjopay callbacks
    path('api/payment/shurjopay/callback/', shurjopay_callback, name='shurjopay_callback'),
    path('api/payment/shurjopay/cancel/',   shurjopay_cancel,   name='shurjopay_cancel'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
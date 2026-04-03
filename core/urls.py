from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from store.views import CartView, ProductView, OrderView, RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/cart/', CartView.as_view(), name='cart'),
    path('api/products/', ProductView.as_view(), name='products'),
    path('api/orders/', OrderView.as_view(), name='orders'),
]
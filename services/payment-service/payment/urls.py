from django.urls import path
from . import views

urlpatterns = [
    path('initiate/',              views.initiate_payment,   name='initiate_payment'),
    path('bkash/callback/',        views.bkash_callback,     name='bkash_callback'),
    path('ssl/success/',           views.ssl_success,        name='ssl_success'),
    path('ssl/fail/',              views.ssl_fail,            name='ssl_fail'),
    path('ssl/cancel/',            views.ssl_cancel,          name='ssl_cancel'),
    path('shurjopay/callback/',    views.shurjopay_callback,  name='shurjopay_callback'),
    path('shurjopay/cancel/',      views.shurjopay_cancel,    name='shurjopay_cancel'),
]

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self): return self.name
    class Meta: verbose_name_plural = "Categories"


class Product(models.Model):
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    image       = models.ImageField(upload_to='products/', blank=True, null=True)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name


class CartItem(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity   = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.product.name} x{self.quantity}"


PAYMENT_METHODS = [
    ('cod',       'Cash on Delivery'),
    ('bkash',     'bKash'),
    ('ssl',       'SSL Commerz'),
    ('shurjopay', 'Shurjopay'),
]
PAYMENT_STATUS = [
    ('pending',   'Pending'),
    ('paid',      'Paid'),
    ('failed',    'Failed'),
    ('cancelled', 'Cancelled'),
]
ORDER_STATUS = [
    ('pending',    'Pending'),
    ('confirmed',  'Confirmed'),
    ('processing', 'Processing'),
    ('shipped',    'Shipped'),
    ('delivered',  'Delivered'),
    ('cancelled',  'Cancelled'),
]
DELIVERY_ZONES = [
    ('inside',  'ঢাকার ভেতরে'),
    ('outside', 'ঢাকার বাইরে'),
]


class Order(models.Model):
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product         = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity        = models.PositiveIntegerField(default=1)
    address         = models.TextField()
    phone           = models.CharField(max_length=20)
    delivery_zone   = models.CharField(max_length=10, choices=DELIVERY_ZONES, default='inside')
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=80)
    payment_method  = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    payment_status  = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    order_status    = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    transaction_id  = models.CharField(max_length=200, blank=True)
    total_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} — {self.product.name}"

    class Meta:
        ordering = ['-created_at']
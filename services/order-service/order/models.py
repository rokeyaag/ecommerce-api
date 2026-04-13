from django.db import models

DELIVERY_ZONES  = [('inside', 'ঢাকার ভেতরে'), ('outside', 'ঢাকার বাইরে')]
ORDER_STATUS    = [('pending','Pending'),('confirmed','Confirmed'),('processing','Processing'),
                   ('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled')]
PAYMENT_STATUS  = [('pending','Pending'),('paid','Paid'),('failed','Failed'),('cancelled','Cancelled')]
PAYMENT_METHODS = [('cod','Cash on Delivery'),('bkash','bKash'),('ssl','SSL Commerz'),('shurjopay','Shurjopay')]

class CartItem(models.Model):
    user_id    = models.IntegerField()
    product_id = models.IntegerField()
    quantity   = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"CartItem user={self.user_id} product={self.product_id} x{self.quantity}"

class Order(models.Model):
    user_id         = models.IntegerField(null=True, blank=True)
    product_id      = models.IntegerField()
    product_name    = models.CharField(max_length=200, default='')
    product_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
    def __str__(self): return f"Order #{self.id} — {self.product_name}"
    class Meta:
        ordering = ['-created_at']

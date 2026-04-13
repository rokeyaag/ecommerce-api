from django.db import models

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

class Payment(models.Model):
    order_id        = models.IntegerField()
    user_id         = models.IntegerField(null=True, blank=True)
    transaction_id  = models.CharField(max_length=200, unique=True)
    payment_method  = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status  = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    currency        = models.CharField(max_length=10, default='BDT')
    payment_url     = models.URLField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} — {self.transaction_id} — {self.payment_status}"

    class Meta:
        ordering = ['-created_at']

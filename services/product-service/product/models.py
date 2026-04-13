from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    image       = models.ImageField(upload_to='products/', blank=True, null=True)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

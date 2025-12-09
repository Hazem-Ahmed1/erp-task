from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.sku} - {self.name}"

class Customer(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Unique Customer ID")
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    email = models.EmailField(blank=True, null=True)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Simple unique ID generation
            last_id = SalesOrder.objects.aggregate(max_id=models.Max('id'))['max_id'] or 0
            self.order_number = f"ORD-{last_id + 1:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class SalesOrderItem(models.Model):
    order = models.ForeignKey(SalesOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Snapshot of price at sale
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total = self.qty * self.price
        super().save(*args, **kwargs)
        # Update order total? Usually done via signal or manual method call to avoid recursion/complexity in save
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'In'),
        ('OUT', 'Out'),
        ('ADJUST', 'Adjustment'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(help_text="Negative for Out, Positive for In")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
         return f"{self.product.sku} - {self.qty} ({self.timestamp})"

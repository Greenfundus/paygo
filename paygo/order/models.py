from django.contrib.auth.models import User
from django.db import models
from product.models import Product

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    insurance_type = models.CharField(max_length=100)
    lga = models.CharField(max_length=100)
    paid_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    order_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='pending', 
                                    choices=[('pending', 'Pending'), 
                                           ('paid', 'Paid'), 
                                           ('failed', 'Failed')])
    payment_reference = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order {self.order.order_number} - {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity

class TransactionHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    type = models.CharField(max_length=100,blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=50,blank=True,null=True)
    method = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return f'{self.user.username} - {self.type} is {self.status}'

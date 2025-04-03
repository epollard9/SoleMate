from django.db import models
from django.contrib.auth.models import User

class Size(models.Model):
    size_code = models.CharField(max_length=10, primary_key=True)  # e.g. SZ09

    def __str__(self):
        return self.size_code

class Shoe(models.Model):
    shoe_number = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    release_date = models.DateField()
    sizes = models.ManyToManyField('Size')
    image = models.ImageField(upload_to='shoe_images/', null=True, blank=True)  # 👈 Add this line

    def __str__(self):
        return f"{self.name} ({self.brand})"


class Order(models.Model):
    order_number = models.CharField(max_length=12, primary_key=True, editable=False)  # e.g. ORD0001
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    shoes = models.ManyToManyField(Shoe, through='OrderItem')

    def save(self, *args, **kwargs):
        if not self.order_number:
            count = Order.objects.count() + 1
            self.order_number = f"ORD{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.shoe.shoe_number} ({self.size.size_code})"

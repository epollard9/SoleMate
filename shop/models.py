from django.db import models
from django.contrib.auth.models import User

class Size(models.Model):
    size_code = models.CharField(max_length=10, primary_key=True)  # e.g. SZ09

    def __str__(self):
        return self.size_code


from django.core.validators import MinValueValidator, MaxValueValidator


class Shoe(models.Model):
    shoe_number = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    release_date = models.DateField()
    last_edit = models.DateField()
    sizes = models.ManyToManyField('Size')
    image = models.ImageField(upload_to='shoe_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_shoes', blank=True)

    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text="Discount as a percentage (e.g., 10.00 for 10%)"
    )

    def __str__(self):
        return f"{self.name} ({self.brand})"

    @property
    def discounted_price(self):
        return self.price * (1 - self.discount / 100)

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

class Review(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # you can later enforce 1–5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.shoe.shoe_number} ({self.rating}/5)"

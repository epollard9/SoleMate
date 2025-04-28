from django.db import models
from django.contrib.auth.models import User
from shop.models import Shoe, Size

class CartItem(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    shoe     = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    size     = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'shoe', 'size')

    def __str__(self):
        return f"{self.user.username} – {self.shoe.name} (Size {self.size.size_code}) × {self.quantity}"

class Order(models.Model):
    user       = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_orders'            # ← avoids clash with shop.Order.user
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} at {self.created_at}"

class OrderItem(models.Model):
    order    = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    shoe     = models.ForeignKey(
        Shoe,
        on_delete=models.CASCADE,
        related_name='cart_order_items'
    )
    size     = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        related_name='cart_order_items_by_size'
    )
    quantity = models.PositiveIntegerField()
    price    = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.shoe.name} (Size {self.size.size_code}) × {self.quantity} @ {self.price}"

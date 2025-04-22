from django.db import models
from django.contrib.auth.models import User
from shop.models import Shoe

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'shoe')

    def __str__(self):
        return f"{self.user.username} - {self.shoe.name} ({self.quantity})"
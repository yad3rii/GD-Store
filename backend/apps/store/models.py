import uuid
from django.conf import settings
from django.db import models
from apps.catalog.models import Game


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="cart_items", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "game")


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="wishlist_items", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "game")


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "pending"),
        ("paid", "paid"),
        ("failed", "failed"),
        ("refunded", "refunded"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)

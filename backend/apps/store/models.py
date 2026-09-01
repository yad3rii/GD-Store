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
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} — {self.game}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="wishlist_items", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "game")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} — {self.game}"


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"
    STATUS_CHOICES = [
        (STATUS_PENDING, "pending"),
        (STATUS_PAID, "paid"),
        (STATUS_FAILED, "failed"),
        (STATUS_REFUNDED, "refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ("order", "game")

    def __str__(self):
        return f"{self.game} in {self.order_id}"

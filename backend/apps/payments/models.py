import uuid
from django.db import models
from apps.store.models import Order


class Payment(models.Model):
    STATUS_CHOICES = [
        ("created", "created"),
        ("succeeded", "succeeded"),
        ("failed", "failed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    provider = models.CharField(max_length=32, default="stripe")  # stripe / liqpay / etc
    provider_payment_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

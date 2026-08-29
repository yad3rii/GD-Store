import uuid

from django.db import models

from apps.store.models import Order


class Payment(models.Model):
    STATUS_CREATED = "created"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_CREATED, "created"),
        (STATUS_SUCCEEDED, "succeeded"),
        (STATUS_FAILED, "failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    provider = models.CharField(max_length=32, default="stripe")  # stripe / liqpay / etc
    provider_payment_id = models.CharField(max_length=128, blank=True, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_CREATED)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    raw_payload = models.JSONField(default=dict, blank=True)  # последний вебхук провайдера, для аудита
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for order {self.order_id} ({self.status})"

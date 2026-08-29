from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "provider", "status", "amount", "created_at"]
    list_filter = ["provider", "status"]
    search_fields = ["id", "provider_payment_id", "order__id"]
    readonly_fields = ["raw_payload", "created_at", "updated_at"]


"""Order closure and promo reservations; caller locks Order before PromoCode."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Order, PromoCode


def close_pending_order(order, new_status):
    """Caller must hold the Order lock inside atomic(). Release at most once."""
    if new_status not in (Order.STATUS_CANCELLED, Order.STATUS_EXPIRED):
        raise ValueError("Unsupported order closure")
    if order.status != Order.STATUS_PENDING:
        return False
    if order.promo_code_id is not None:
        changed = PromoCode.objects.filter(
            pk=order.promo_code_id, times_used__gt=0,
        ).update(times_used=F("times_used") - 1)
        if changed != 1:
            raise ValidationError("Счётчик промокода требует сверки. Заказ не изменён.")
    order.status = new_status
    order.save(update_fields=["status"])
    return True


def expire_order_if_due(order, now=None):
    now = now if now is not None else timezone.now()
    if (order.status != Order.STATUS_PENDING or order.expires_at is None
            or order.expires_at > now):
        return False
    return close_pending_order(order, Order.STATUS_EXPIRED)


def expire_pending_orders(promo_id=None):
    """Shared by scheduled command and on-demand promo validation.

    No PromoCode lock is held while acquiring an existing Order lock.
    Fetch a batch completely before writes (no parallel ODBC cursors).
    """
    now = timezone.now()
    count = 0
    last_pk = None
    while True:
        candidates = Order.objects.filter(
            status=Order.STATUS_PENDING, expires_at__lte=now,
        )
        if promo_id is not None:
            candidates = candidates.filter(promo_code_id=promo_id)
        if last_pk is not None:
            candidates = candidates.filter(pk__gt=last_pk)
        ids = list(candidates.order_by("pk").values_list("pk", flat=True)[:200])
        if not ids:
            break
        for order_id in ids:
            with transaction.atomic():
                order = Order.objects.select_for_update().filter(pk=order_id).first()
                if order is not None and expire_order_if_due(order, now):
                    count += 1
        last_pk = ids[-1]
    return count

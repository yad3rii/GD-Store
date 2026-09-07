import hashlib
import hmac
import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Game
from apps.library.models import LibraryEntry
from apps.store.models import CartItem, Order

from .models import Payment

User = get_user_model()


def sign(secret, body_bytes):
    return hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()


class PaymentsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.friend = User.objects.create_user(username="friend", password="pass12345")
        self.other = User.objects.create_user(username="stranger", password="pass12345")
        self.game = Game.objects.create(
            title="Game", slug="game", price=Decimal("15.00"), is_published=True
        )
        self.client.force_authenticate(self.user)
        CartItem.objects.create(user=self.user, game=self.game)
        resp = self.client.post("/api/v1/store/cart/checkout/")
        self.order = Order.objects.get(id=resp.data["id"])

    def test_create_payment_for_own_pending_order(self):
        resp = self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("checkout_url", resp.data)
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)

    def test_create_payment_for_someone_elses_order_is_404(self):
        self.client.force_authenticate(self.other)
        resp = self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_payment_reuses_existing_non_succeeded_payment(self):
        self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        resp = self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)

    def test_webhook_success_marks_order_paid_and_grants_library(self):
        self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        provider_payment_id = Payment.objects.get(order=self.order).provider_payment_id

        payload = {"provider_payment_id": provider_payment_id, "status": "succeeded"}
        resp = self.client.post("/api/v1/payments/webhook/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertTrue(LibraryEntry.objects.filter(user=self.user, game=self.game).exists())

    def test_webhook_is_idempotent(self):
        self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        provider_payment_id = Payment.objects.get(order=self.order).provider_payment_id
        payload = {"provider_payment_id": provider_payment_id, "status": "succeeded"}

        self.client.post("/api/v1/payments/webhook/", payload, format="json")
        self.client.post("/api/v1/payments/webhook/", payload, format="json")

        self.assertEqual(LibraryEntry.objects.filter(user=self.user, game=self.game).count(), 1)

    def test_webhook_gift_order_grants_recipient(self):
        CartItem.objects.create(user=self.user, game=self.game)
        # предыдущий заказ уже забрал игру из корзины покупателя — оформим новую игру заново
        game2 = Game.objects.create(title="Game 2", slug="game-2", price=Decimal("5.00"), is_published=True)
        CartItem.objects.create(user=self.user, game=game2)
        checkout_resp = self.client.post(
            "/api/v1/store/cart/checkout/", {"recipient_username": "friend"}
        )
        gift_order = Order.objects.get(id=checkout_resp.data["id"])

        self.client.post("/api/v1/payments/create/", {"order_id": str(gift_order.id)})
        provider_payment_id = Payment.objects.get(order=gift_order).provider_payment_id
        payload = {"provider_payment_id": provider_payment_id, "status": "succeeded"}
        resp = self.client.post("/api/v1/payments/webhook/", payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(LibraryEntry.objects.filter(user=self.friend, game=game2).exists())
        self.assertFalse(LibraryEntry.objects.filter(user=self.user, game=game2).exists())

    def test_webhook_failed_status_marks_order_failed(self):
        self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        provider_payment_id = Payment.objects.get(order=self.order).provider_payment_id
        payload = {"provider_payment_id": provider_payment_id, "status": "failed"}
        resp = self.client.post("/api/v1/payments/webhook/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_FAILED)

    @override_settings(PAYMENT_WEBHOOK_SECRET="testsecret")
    def test_webhook_rejects_bad_signature(self):
        self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        provider_payment_id = Payment.objects.get(order=self.order).provider_payment_id
        body = json.dumps({"provider_payment_id": provider_payment_id, "status": "succeeded"}).encode()

        resp = self.client.generic(
            "POST", "/api/v1/payments/webhook/", data=body,
            content_type="application/json", HTTP_X_SIGNATURE="wrong",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(PAYMENT_WEBHOOK_SECRET="testsecret")
    def test_webhook_accepts_correct_signature(self):
        self.client.post("/api/v1/payments/create/", {"order_id": str(self.order.id)})
        provider_payment_id = Payment.objects.get(order=self.order).provider_payment_id
        body = json.dumps({"provider_payment_id": provider_payment_id, "status": "succeeded"}).encode()
        signature = sign("testsecret", body)

        resp = self.client.generic(
            "POST", "/api/v1/payments/webhook/", data=body,
            content_type="application/json", HTTP_X_SIGNATURE=signature,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

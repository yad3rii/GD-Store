import hashlib
import hmac
import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Friendship
from apps.catalog.models import Game
from apps.library.models import LibraryEntry
from apps.store.models import CartItem, Order

from .models import Payment


User = get_user_model()
TEST_WEBHOOK_SECRET = "testsecret"


def sign(secret, body_bytes):
    return hmac.new(
        secret.encode("utf-8"),
        body_bytes,
        hashlib.sha256,
    ).hexdigest()


@override_settings(PAYMENT_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
class PaymentsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            password="pass12345",
        )
        self.friend = User.objects.create_user(
            username="friend",
            password="pass12345",
        )
        self.other = User.objects.create_user(
            username="stranger",
            password="pass12345",
        )

        Friendship.objects.create(
            from_user=self.user,
            to_user=self.friend,
            status="accepted",
        )

        self.game = Game.objects.create(
            title="Game",
            slug="game",
            price=Decimal("15.00"),
            is_published=True,
        )

        self.client.force_authenticate(self.user)
        CartItem.objects.create(user=self.user, game=self.game)

        response = self.client.post("/api/v1/store/cart/checkout/")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )
        self.order = Order.objects.get(id=response.data["id"])

    def create_payment(self, order=None):
        order = order if order is not None else self.order

        response = self.client.post(
            "/api/v1/payments/create/",
            {"order_id": str(order.id)},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        return Payment.objects.get(order=order)

    def post_webhook(self, payload):
        body = json.dumps(payload).encode("utf-8")

        return self.client.generic(
            "POST",
            "/api/v1/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE=sign(TEST_WEBHOOK_SECRET, body),
        )

    def assert_payment_unchanged(self, payment):
        self.order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(self.order.status, Order.STATUS_PENDING)
        self.assertEqual(payment.status, Payment.STATUS_CREATED)
        self.assertEqual(payment.raw_payload, {})
        self.assertFalse(
            LibraryEntry.objects.filter(
                user=self.user,
                game=self.game,
            ).exists()
        )

    def test_create_payment_for_own_pending_order(self):
        response = self.client.post(
            "/api/v1/payments/create/",
            {"order_id": str(self.order.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("checkout_url", response.data)
        self.assertEqual(
            Payment.objects.filter(order=self.order).count(),
            1,
        )

    def test_create_payment_for_someone_elses_order_is_404(self):
        self.client.force_authenticate(self.other)

        response = self.client.post(
            "/api/v1/payments/create/",
            {"order_id": str(self.order.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(
            Payment.objects.filter(order=self.order).exists()
        )

    def test_create_payment_reuses_existing_non_succeeded_payment(self):
        first_payment = self.create_payment()
        second_payment = self.create_payment()

        self.assertEqual(first_payment.pk, second_payment.pk)
        self.assertEqual(
            Payment.objects.filter(order=self.order).count(),
            1,
        )

    def test_webhook_success_marks_order_paid_and_grants_library(self):
        payment = self.create_payment()

        response = self.post_webhook({
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)
        self.assertTrue(
            LibraryEntry.objects.filter(
                user=self.user,
                game=self.game,
            ).exists()
        )

    def test_webhook_is_idempotent(self):
        payment = self.create_payment()
        payload = {
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        }

        first_response = self.post_webhook(payload)
        second_response = self.post_webhook(payload)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            LibraryEntry.objects.filter(
                user=self.user,
                game=self.game,
            ).count(),
            1,
        )

        self.order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)

    def test_webhook_gift_order_grants_recipient(self):
        game2 = Game.objects.create(
            title="Game 2",
            slug="game-2",
            price=Decimal("5.00"),
            is_published=True,
        )

        CartItem.objects.create(user=self.user, game=self.game)
        CartItem.objects.create(user=self.user, game=game2)

        checkout_response = self.client.post(
            "/api/v1/store/cart/checkout/",
            {"recipient_username": self.friend.username},
        )

        self.assertEqual(
            checkout_response.status_code,
            status.HTTP_201_CREATED,
            checkout_response.data,
        )

        gift_order = Order.objects.get(id=checkout_response.data["id"])
        payment = self.create_payment(gift_order)

        response = self.post_webhook({
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        gift_order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(gift_order.status, Order.STATUS_PAID)
        self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)

        for game in (self.game, game2):
            self.assertTrue(
                LibraryEntry.objects.filter(
                    user=self.friend,
                    game=game,
                ).exists()
            )
            self.assertFalse(
                LibraryEntry.objects.filter(
                    user=self.user,
                    game=game,
                ).exists()
            )

    def test_webhook_failed_keeps_order_pending(self):
        payment = self.create_payment()

        response = self.post_webhook({
            "provider_payment_id": payment.provider_payment_id,
            "status": "failed",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(self.order.status, Order.STATUS_PENDING)
        self.assertEqual(payment.status, Payment.STATUS_FAILED)
        self.assertFalse(
            LibraryEntry.objects.filter(
                user=self.user,
                game=self.game,
            ).exists()
        )

    def test_webhook_rejects_bad_signature(self):
        payment = self.create_payment()
        body = json.dumps({
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        }).encode("utf-8")

        self.client.force_authenticate(user=None)

        response = self.client.generic(
            "POST",
            "/api/v1/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE="wrong",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_payment_unchanged(payment)

    def test_webhook_accepts_correct_signature(self):
        payment = self.create_payment()

        # Провайдер не входит в аккаунт пользователя.
        self.client.force_authenticate(user=None)

        response = self.post_webhook({
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)
        self.assertTrue(
            LibraryEntry.objects.filter(
                user=self.user,
                game=self.game,
            ).exists()
        )

    def test_webhook_rejects_missing_secret(self):
        payment = self.create_payment()
        payload = {
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        }

        self.client.force_authenticate(user=None)

        # Даже подписанный запрос нельзя принять без серверного секрета.
        with override_settings(PAYMENT_WEBHOOK_SECRET=""):
            response = self.post_webhook(payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_payment_unchanged(payment)

    def test_webhook_rejects_missing_signature(self):
        payment = self.create_payment()
        body = json.dumps({
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        }).encode("utf-8")

        self.client.force_authenticate(user=None)

        response = self.client.generic(
            "POST",
            "/api/v1/payments/webhook/",
            data=body,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_payment_unchanged(payment)

    def test_webhook_rejects_incorrect_signature_without_grant(self):
        payment = self.create_payment()
        body = json.dumps({
            "provider_payment_id": payment.provider_payment_id,
            "status": "succeeded",
        }).encode("utf-8")

        self.client.force_authenticate(user=None)

        # Формат подписи правильный, но использован чужой секрет.
        response = self.client.generic(
            "POST",
            "/api/v1/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE=sign("incorrect-secret", body),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_payment_unchanged(payment)
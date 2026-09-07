from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Game
from apps.library.models import LibraryEntry

from .models import CartItem, Order, PromoCode

User = get_user_model()


def make_game(title="Test Game", price="10.00", published=True):
    return Game.objects.create(
        title=title,
        slug=title.lower().replace(" ", "-"),
        price=Decimal(price),
        is_published=published,
    )


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.client.force_authenticate(self.user)
        self.game = make_game()

    def test_add_and_list_cart(self):
        resp = self.client.post("/api/v1/store/cart/", {"game": str(self.game.id)})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)

        resp = self.client.get("/api/v1/store/cart/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_adding_same_game_twice_is_idempotent(self):
        # Повторное добавление той же игры не создаёт вторую позицию и не считается ошибкой.
        self.client.post("/api/v1/store/cart/", {"game": str(self.game.id)})
        resp = self.client.post("/api/v1/store/cart/", {"game": str(self.game.id)})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)

    def test_cannot_add_already_owned_game(self):
        LibraryEntry.objects.create(user=self.user, game=self.game)
        resp = self.client.post("/api/v1/store/cart/", {"game": str(self.game.id)})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class CheckoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.friend = User.objects.create_user(username="friend", password="pass12345")
        self.client.force_authenticate(self.user)
        self.game_a = make_game("Game A", "20.00")
        self.game_b = make_game("Game B", "30.00")
        CartItem.objects.create(user=self.user, game=self.game_a)
        CartItem.objects.create(user=self.user, game=self.game_b)

    def test_checkout_creates_order_and_empties_cart(self):
        resp = self.client.post("/api/v1/store/cart/checkout/")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(resp.data["total"]), Decimal("50.00"))
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)
        order = Order.objects.get(id=resp.data["id"])
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertIsNotNone(order.expires_at)
        self.assertEqual(order.items.count(), 2)

    def test_checkout_empty_cart_rejected(self):
        CartItem.objects.filter(user=self.user).delete()
        resp = self.client.post("/api/v1/store/cart/checkout/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_with_valid_promo_applies_discount(self):
        promo = PromoCode.objects.create(code="SALE10", discount_percent=10)
        resp = self.client.post("/api/v1/store/cart/checkout/", {"promo_code": "SALE10"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(resp.data["subtotal"]), Decimal("50.00"))
        self.assertEqual(Decimal(resp.data["discount_total"]), Decimal("5.00"))
        self.assertEqual(Decimal(resp.data["total"]), Decimal("45.00"))
        promo.refresh_from_db()
        self.assertEqual(promo.times_used, 1)

    def test_checkout_with_invalid_promo_rejected(self):
        resp = self.client.post("/api/v1/store/cart/checkout/", {"promo_code": "NOPE"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_expired_promo_rejected(self):
        PromoCode.objects.create(
            code="OLD", discount_percent=50, valid_until=timezone.now() - timezone.timedelta(days=1)
        )
        resp = self.client.post("/api/v1/store/cart/checkout/", {"promo_code": "OLD"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_as_gift_sets_recipient(self):
        resp = self.client.post("/api/v1/store/cart/checkout/", {"recipient_username": "friend"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["recipient"], "friend")
        self.assertTrue(resp.data["is_gift"])

    def test_checkout_gift_to_self_rejected(self):
        resp = self.client.post("/api/v1/store/cart/checkout/", {"recipient_username": "buyer"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_skips_games_recipient_already_owns(self):
        LibraryEntry.objects.create(user=self.friend, game=self.game_a)
        resp = self.client.post("/api/v1/store/cart/checkout/", {"recipient_username": "friend"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data["items"]), 1)
        self.assertEqual(resp.data["items"][0]["game"]["id"], str(self.game_b.id))


class OrderActionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.client.force_authenticate(self.user)
        self.game = make_game()
        CartItem.objects.create(user=self.user, game=self.game)
        resp = self.client.post("/api/v1/store/cart/checkout/")
        self.order_id = resp.data["id"]

    def test_cancel_pending_order(self):
        resp = self.client.post(f"/api/v1/store/orders/{self.order_id}/cancel/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], Order.STATUS_CANCELLED)

    def test_cannot_cancel_twice(self):
        self.client.post(f"/api/v1/store/orders/{self.order_id}/cancel/")
        resp = self.client.post(f"/api/v1/store/orders/{self.order_id}/cancel/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_refund_unpaid_order(self):
        resp = self.client.post(f"/api/v1/store/orders/{self.order_id}/refund/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refund_paid_order_removes_library_entry(self):
        order = Order.objects.get(id=self.order_id)
        order.status = Order.STATUS_PAID
        order.save(update_fields=["status"])
        LibraryEntry.objects.create(user=self.user, game=self.game)

        resp = self.client.post(f"/api/v1/store/orders/{self.order_id}/refund/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], Order.STATUS_REFUNDED)
        self.assertFalse(LibraryEntry.objects.filter(user=self.user, game=self.game).exists())

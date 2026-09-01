from django.contrib import admin

from .models import CartItem, Order, OrderItem, Wishlist


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["game", "price_at_purchase"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "user__username", "user__email"]
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["user", "game", "added_at"]
    search_fields = ["user__username", "game__title"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "game", "added_at"]
    search_fields = ["user__username", "game__title"]

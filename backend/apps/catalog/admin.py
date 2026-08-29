from django.contrib import admin
from .models import Game, Genre, Tag, Developer, Publisher, Screenshot, SystemRequirement


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(SystemRequirement)
class SystemRequirementAdmin(admin.ModelAdmin):
    list_display = ["game", "os", "cpu", "ram", "gpu", "storage"]
    search_fields = ["game__title", "os", "cpu", "gpu"]
    autocomplete_fields = ["game"]


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "discount_percent", "final_price_display", "is_published", "release_date"]
    list_filter = ["is_published", "genres"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ScreenshotInline]

    @admin.display(description="Цена со скидкой")
    def final_price_display(self, obj):
        return obj.final_price
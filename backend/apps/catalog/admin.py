from django.contrib import admin
from .models import (
    Developer,
    Game,
    Genre,
    Publisher,
    Screenshot,
    SystemRequirement,
    Tag,
)


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 1


class SystemRequirementInline(admin.StackedInline):
    model = SystemRequirement
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "discount_percent", "is_published", "release_date"]
    list_filter = ["is_published", "genres", "tags"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ScreenshotInline, SystemRequirementInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Tag)
admin.site.register(Developer)
admin.site.register(Publisher)
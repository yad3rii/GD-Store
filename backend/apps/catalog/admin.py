from django.contrib import admin
from .models import Game, Genre, Tag, Developer, Publisher, Screenshot, SystemRequirement

admin.site.register(Genre)
admin.site.register(Tag)
admin.site.register(Developer)
admin.site.register(Publisher)
admin.site.register(SystemRequirement)


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "discount_percent", "is_published", "release_date"]
    list_filter = ["is_published", "genres"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ScreenshotInline]

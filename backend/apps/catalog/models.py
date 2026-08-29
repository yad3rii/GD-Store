import uuid
from decimal import Decimal
from django.core.validators import MaxValueValidator
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Developer(models.Model):
    name = models.CharField(max_length=128)


class Publisher(models.Model):
    name = models.CharField(max_length=128)


class Game(models.Model):
    """Основная карточка товара (как страница игры в Steam)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="games/covers/", blank=True, null=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    release_date = models.DateField(null=True, blank=True)

    genres = models.ManyToManyField(Genre, related_name="games", blank=True)
    tags = models.ManyToManyField(Tag, related_name="games", blank=True)
    developers = models.ManyToManyField(Developer, related_name="games", blank=True)
    publishers = models.ManyToManyField(Publisher, related_name="games", blank=True)

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_price(self):
      
        discount = Decimal(self.discount_percent) / Decimal(100)
        return (self.price * (Decimal(1) - discount)).quantize(Decimal("0.01"))

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Screenshot(models.Model):
    game = models.ForeignKey(Game, related_name="screenshots", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="games/screenshots/")
    order = models.PositiveSmallIntegerField(default=0)


class SystemRequirement(models.Model):
    KIND_CHOICES = [("min", "minimum"), ("rec", "recommended")]
    game = models.OneToOneField(Game, related_name="requirements", on_delete=models.CASCADE)
    os = models.CharField(max_length=200, blank=True)
    cpu = models.CharField(max_length=200, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    gpu = models.CharField(max_length=200, blank=True)
    storage = models.CharField(max_length=50, blank=True)

from django.db import models

from apps.pages.models import SEOMixin


class Category(models.Model):
    name = models.CharField(max_length=100, help_text="Category name (e.g. Sweeteners).")
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-friendly identifier. Auto-generated from name.")
    description = models.TextField(blank=True, help_text="Optional short description shown on the category page.")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, help_text="Category thumbnail image.")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first).")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Product(SEOMixin):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="The category this product belongs to.",
    )
    name = models.CharField(max_length=200, help_text="Full product name.")
    slug = models.SlugField(max_length=220, unique=True, help_text="URL-friendly identifier. Auto-generated from name.")
    description = models.TextField(blank=True, help_text="Product description shown on the detail page.")
    specifications = models.TextField(blank=True, help_text="Technical specs, purity, CAS number, etc. Plain text or simple formatting.")
    image = models.ImageField(upload_to="products/", blank=True, null=True, help_text="Main product image.")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this product from the website.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.pages.models import SEOMixin
from apps.utils.images import process_image


class Certification(models.Model):
    name = models.CharField(max_length=100, help_text="Certification name (e.g. Halal, Kosher, Non-GMO).")
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-friendly identifier used in filters.")
    order = models.PositiveIntegerField(default=0, help_text="Display order in the filter sidebar.")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=100, help_text="Application sector (e.g. Bakery, Dairy, Beverages).")
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-friendly identifier used in filters.")
    order = models.PositiveIntegerField(default=0, help_text="Display order in the filter sidebar.")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, help_text="Category name (e.g. Sweeteners).")
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-friendly identifier. Auto-generated from name.")
    description = models.TextField(blank=True, help_text="Optional short description shown on the category page.")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, help_text="Category thumbnail image.")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first).")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    # Slugs that would shadow fixed routes under /products/
    _RESERVED_SLUGS = {'search', 'api'}

    def clean(self):
        if self.slug in self._RESERVED_SLUGS:
            raise ValidationError({'slug': f'"{self.slug}" is a reserved URL segment and cannot be used as a category slug.'})

    def save(self, *args, **kwargs):
        process_image(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


ORIGIN_CHOICES = [
    ("plant",        "Plant"),
    ("animal",       "Animal"),
    ("synthetic",    "Synthetic"),
    ("mineral",      "Mineral"),
    ("fermentation", "Fermentation"),
]


class Product(SEOMixin):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="The category this product belongs to.",
    )
    name = models.CharField(max_length=200, help_text="Full product name.")
    slug = models.SlugField(max_length=220, unique=True, help_text="URL-friendly identifier. Auto-generated from name.")

    # Identification
    cas_number = models.CharField(
        max_length=50, blank=True,
        help_text="CAS Registry Number (e.g. 9000-07-1). Used heavily by B2B buyers.",
        verbose_name="CAS Number",
    )
    e_number = models.CharField(
        max_length=20, blank=True,
        help_text="EU food additive code (e.g. E407). Leave blank if not applicable.",
        verbose_name="E-Number",
    )
    alternative_names = models.CharField(
        max_length=500, blank=True,
        help_text="Synonyms and trade names for this product. Improves search.",
    )

    # Description
    description = models.TextField(blank=True, help_text="Product description shown on the detail page.")
    specifications = models.TextField(blank=True, help_text="Technical specs, purity, viscosity, shelf life, etc.")

    # Classification
    origin = models.CharField(
        max_length=20, choices=ORIGIN_CHOICES, blank=True,
        help_text="Source origin — used for Halal/Kosher/Vegan filtering.",
    )
    available_forms = models.CharField(
        max_length=200, blank=True,
        help_text="Physical forms available (e.g. Powder, Granule, Liquid). Comma-separated.",
    )

    # Relations
    certifications = models.ManyToManyField(
        Certification, blank=True,
        help_text="Quality and compliance certifications this product holds.",
    )
    applications = models.ManyToManyField(
        Application, blank=True,
        help_text="Industry sectors or end-use applications for this product.",
    )

    # Media
    image = models.ImageField(upload_to="products/", blank=True, null=True, help_text="Main product image.")
    datasheet = models.FileField(
        upload_to="datasheets/", blank=True, null=True,
        help_text="Technical data sheet or MSDS (PDF). Displayed as a download on the product page.",
    )

    is_active = models.BooleanField(default=True, db_index=True, help_text="Uncheck to hide this product from the website.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    search_vector = SearchVectorField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        process_image(self.image)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.category.slug, self.slug])

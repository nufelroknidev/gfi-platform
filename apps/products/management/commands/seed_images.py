"""
Management command: seed_images
Copies placeholder images from static/img/ into media/ and assigns them
to categories, products, and news posts for local development/preview.
"""

import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.news.models import Post as NewsPost
from apps.products.models import Category, Product

SRC = settings.BASE_DIR / "static" / "img"

CATEGORY_IMAGES = {
    "sweeteners":             "cat-sweeteners.jpg",
    "thickeners-stabilisers": "cat-thickeners.jpg",
    "preservatives":          "cat-preservatives.jpg",
    "vitamins-nutrients":     "cat-vitamins.jpg",
    "amino-acids-proteins":   "cat-amino-acids.jpg",
    "plant-extracts":         "cat-plant-extracts.jpg",
}

PRODUCT_IMAGES = {
    "carrageenan-kappa":         "prod-carrageenan.jpg",
    "curcumin-extract-95":       "prod-curcumin.jpg",
    "green-tea-extract-egcg-50": "prod-green-tea.jpg",
    "l-glutamine":               "prod-l-glutamine.jpg",
    "l-lysine-hcl":              "prod-l-lysine.jpg",
    "maltitol":                  "prod-maltitol.jpg",
    "potassium-sorbate":         "prod-potassium-sorbate.jpg",
    "sodium-benzoate":           "prod-sodium-benzoate.jpg",
    "stevia-extract-reb-a-97":   "prod-stevia.jpg",
    "sucralose":                 "prod-sucralose.jpg",
    "vitamin-c-ascorbic-acid":   "prod-vitamin-c.jpg",
    "xanthan-gum":               "prod-xanthan-gum.jpg",
    "zinc-sulphate-monohydrate": "prod-zinc-sulphate.jpg",
}

NEWS_IMAGES = {
    "gfi-attends-thaifex-2025":          "news-thaifex.jpg",
    "new-partnership-european-supplier": "news-partnership.jpg",
    "q1-2025-product-catalogue-update":  "news-catalogue.jpg",
}


def copy_and_assign(src_filename, dest_subdir, instance, field_name):
    src = SRC / src_filename
    if not src.exists():
        return f"  MISSING source: {src_filename}"
    dest_dir = settings.MEDIA_ROOT / dest_subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src_filename
    shutil.copy2(src, dest)
    setattr(instance, field_name, f"{dest_subdir}/{src_filename}")
    instance.save(update_fields=[field_name])
    return f"  OK  {instance} -> {dest_subdir}/{src_filename}"


class Command(BaseCommand):
    help = "Seed placeholder images for categories, products, and news posts."

    def handle(self, *args, **options):
        self.stdout.write("=== Categories ===")
        for cat in Category.objects.all():
            img = CATEGORY_IMAGES.get(cat.slug)
            if img:
                self.stdout.write(copy_and_assign(img, "categories", cat, "image"))
            else:
                self.stdout.write(f"  SKIP  no mapping for slug '{cat.slug}'")

        self.stdout.write("\n=== Products ===")
        for prod in Product.objects.all():
            img = PRODUCT_IMAGES.get(prod.slug)
            if img:
                self.stdout.write(copy_and_assign(img, "products", prod, "image"))
            else:
                self.stdout.write(f"  SKIP  no mapping for slug '{prod.slug}'")

        self.stdout.write("\n=== News Posts ===")
        for post in NewsPost.objects.all():
            img = NEWS_IMAGES.get(post.slug)
            if img:
                self.stdout.write(copy_and_assign(img, "news", post, "featured_image"))
            else:
                self.stdout.write(f"  SKIP  no mapping for slug '{post.slug}'")

        self.stdout.write(self.style.SUCCESS("\nDone."))

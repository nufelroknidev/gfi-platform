"""
Management command: fetch_product_images

Searches Wikimedia Commons for a freely-licensed image for each product
(or a specified subset), downloads it, and saves it via Django's storage
backend (local media/ in dev, S3 in production).

Usage:
    # Dry-run — print matches without saving
    python manage.py fetch_product_images --dry-run

    # Process specific products by ID
    python manage.py fetch_product_images --ids 737 853 842 795 830

    # Process all products without images
    python manage.py fetch_product_images --all

    # Skip products that already have an image
    python manage.py fetch_product_images --all --skip-existing
"""

import time
from io import BytesIO

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.products.models import Product

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "GFI-Website-ImageFetcher/1.0 (nufel.rokni.dev@gmail.com)"}

# Words in file titles that indicate the image is NOT of the substance itself
_BAD_TITLE_WORDS = {
    "people", "person", "portrait", "meeting", "conference", "map",
    "logo", "flag", "graph", "chart", "diagram", "structure", "formula",
    "molecule", "skeletal", "synthesis", "reaction", "mechanism",
    "ball", "stick", "3d", "2d", "model", "conjugation", "zwitterion",
    "esempio", "example", "isomer", "enantiomer", "stereoisomer",
}

# Aspect ratios outside this range are almost certainly diagrams, not photos
_MIN_RATIO = 0.5   # taller than 2:1 landscape
_MAX_RATIO = 3.0   # wider than 3:1 landscape


def _score_candidate(title: str, mime: str, width: int, height: int) -> int:
    """Lower score = better candidate. Returns 999 to discard entirely."""
    title_lower = title.lower()

    # Hard reject: SVG or any bad keyword in title
    if mime == "image/svg+xml":
        return 999
    if any(w in title_lower for w in _BAD_TITLE_WORDS):
        return 999

    # Hard reject: too many hyphen segments after stripping the file: prefix
    # e.g. "File:beta-carotene-fieser-kuhn-esempio.png" → 4 segments = diagram
    stem = title_lower.replace("file:", "").rsplit(".", 1)[0]
    if stem.count("-") >= 4:
        return 999

    # Hard reject: extreme aspect ratio (diagrams are often very wide and short)
    if height > 0:
        ratio = width / height
        if ratio < _MIN_RATIO or ratio > _MAX_RATIO:
            return 999

    score = 0
    # Prefer JPEG (real photos) over PNG (often diagrams)
    if mime == "image/jpeg":
        score += 0
    elif mime == "image/png":
        score += 1
    else:
        score += 2

    # Prefer larger images (real photos tend to be bigger)
    pixels = width * height
    if pixels >= 400_000:
        score += 0
    elif pixels >= 100_000:
        score += 1
    else:
        score += 2

    return score


def _pick_best(pages: dict) -> dict | None:
    """Return the highest-quality candidate from a Wikimedia Commons pages dict."""
    candidates = []
    for page in pages.values():
        info = page.get("imageinfo", [{}])[0]
        mime = info.get("mime", "")
        if not mime.startswith("image/"):
            continue
        width = info.get("thumbwidth") or info.get("width") or 0
        height = info.get("thumbheight") or info.get("height") or 0
        title = page.get("title", "")
        score = _score_candidate(title, mime, width, height)
        if score < 999:
            candidates.append((score, page["pageid"], {
                "title": title,
                "url": info.get("thumburl") or info.get("url"),
                "mime": mime,
            }))
    candidates.sort(key=lambda x: (x[0], x[1]))
    return candidates[0][2] if candidates else None


def _query_commons(search: str) -> dict | None:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrsearch": search,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|dimensions",
        "iiurlwidth": 800,
    }
    resp = requests.get(COMMONS_API, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    return _pick_best(pages)


def search_commons(product_name: str, cas: str = "") -> dict | None:
    """Try progressively broader queries until a good image is found."""
    # Strip common parenthetical suffixes to get a cleaner base name
    # e.g. "Ascorbic Acid (Vitamin C)" → "Ascorbic Acid"
    base = product_name.split("(")[0].strip()
    # Drop trailing descriptor words that confuse the search
    for suffix in (" Powder", " Extract", " Refined", " Semi-Refined", " Blend", " Flakes"):
        if base.endswith(suffix):
            base = base[: -len(suffix)].strip()

    queries = [product_name, base, f"{base} powder", f"{base} crystal", f"{base} food"]
    if cas:
        queries.append(cas)
    # Deduplicate while preserving order
    seen, unique = set(), []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    for q in unique:
        result = _query_commons(q)
        if result:
            return result
    return None


def download_image(url: str) -> bytes:
    resp = requests.get(url, headers=HEADERS, timeout=30, stream=True)
    resp.raise_for_status()
    buf = BytesIO()
    for chunk in resp.iter_content(8192):
        buf.write(chunk)
    return buf.getvalue()


def ext_for_mime(mime: str) -> str:
    return {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(mime, "jpg")


class Command(BaseCommand):
    help = "Fetch freely-licensed images from Wikimedia Commons for products."

    def add_arguments(self, parser):
        parser.add_argument("--ids", nargs="+", type=int, help="Product IDs to process.")
        parser.add_argument("--all", action="store_true", help="Process all active products.")
        parser.add_argument("--skip-existing", action="store_true", help="Skip products that already have an image.")
        parser.add_argument("--dry-run", action="store_true", help="Search only — do not download or save.")

    def handle(self, *args, **options):
        qs = Product.objects.filter(is_active=True).defer("search_vector").order_by("name")

        if options["ids"]:
            qs = qs.filter(pk__in=options["ids"])
        elif not options["all"]:
            self.stderr.write("Pass --ids <id...> or --all. Use --dry-run to preview.")
            return

        if options["skip_existing"]:
            qs = qs.exclude(image="")

        products = list(qs)
        self.stdout.write(f"Processing {len(products)} product(s)  [dry_run={options['dry_run']}]\n")

        total_time = 0.0
        success = 0

        for product in products:
            t0 = time.perf_counter()
            self.stdout.write(f"  {product.name} ...", ending=" ")
            self.stdout.flush()

            result = search_commons(product.name, product.cas_number)
            if not result:
                self.stdout.write(self.style.WARNING("NOT FOUND"))
                continue

            elapsed_search = time.perf_counter() - t0

            if options["dry_run"]:
                self.stdout.write(self.style.SUCCESS(f"FOUND  {result['url']}"))
                continue

            try:
                data = download_image(result["url"])
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"DOWNLOAD ERROR: {exc}"))
                continue

            ext = ext_for_mime(result["mime"])
            filename = f"{product.slug}.{ext}"
            product.image.save(filename, ContentFile(data), save=True)

            elapsed_total = time.perf_counter() - t0
            total_time += elapsed_total
            success += 1
            self.stdout.write(self.style.SUCCESS(f"SAVED  ({elapsed_total:.1f}s)  {filename}"))

            # Be a polite crawler — 0.5 s between requests
            time.sleep(0.5)

        if not options["dry_run"] and success:
            avg = total_time / success
            self.stdout.write(f"\nDone: {success}/{len(products)} images saved.")
            self.stdout.write(f"  Average time per image: {avg:.1f}s")
            self.stdout.write(f"  Estimated time for all 142 products: {avg * 142 / 60:.1f} min")

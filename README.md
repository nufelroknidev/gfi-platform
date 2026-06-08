# GFI — General Food Industry Co., Ltd.

Production B2B website for a Thai food additives importer/distributor. Presents a searchable product catalogue, publishes industry news, and routes customer inquiries through a rate-limited contact form. No e-commerce.

**Live:** https://www.generalfoodindustry.com

---

## Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.13 / Django 6.0 |
| Database | PostgreSQL (self-hosted on EC2) |
| File storage | AWS S3 (static + media) + CloudFront CDN (PriceClass_200) |
| REST API | Django REST Framework + django-filter |
| Frontend | Django templates + Bootstrap 5.3.3 + vanilla JS |
| Admin UI | django-jazzmin + django-summernote |
| Env management | django-environ |
| Dependency management | Poetry 2.x |
| Deployment | AWS EC2 t4g.micro — nginx + gunicorn (systemd) |
| CI/CD | GitHub Actions → `deploy/aws` branch |
| Dev tooling | django-debug-toolbar + django-browser-reload |

---

## Features

**Product catalogue**
- Categories, certifications, applications, origin (plant/animal/synthetic/mineral/fermentation)
- Faceted sidebar filters: certification, application, origin checkboxes/radios
- Client-side category text filter (no server round-trip)
- PDF technical datasheet download per product
- Specifications rendered as a table via `parse_specs` custom template tag (pipe-separated storage format)

**Search**
- PostgreSQL `SearchVector` with weighted fields: name (A), CAS/E-number/alt names (B), description (C), specs (D); GIN index
- `websearch_to_tsquery`; CAS/E-number normalisation (strips hyphens, normalises `e407` → `E407`)
- Live typeahead via `/products/api/suggest/` JSON endpoint
- Falls back to `icontains` on SQLite (dev/test)

**Partial page updates (vanilla JS)**
- Filter and category changes: full section swap with CSS fade animation, URL updated via `pushState`
- Live search: debounced (350 ms), updates only the product grid — input focus never lost
- Load More: appends next page to the grid without a full swap
- All three behaviours use `fetch()` with `X-GFI-Partial` header to request server-rendered partials

**REST API**
- Read-only endpoints: `/api/products/`, `/api/products/<slug>/`, `/api/categories/`
- Query params: `?search=`, `?category=`, `?certification=`, `?ordering=`
- Category list annotated with `product_count`; paginated at 20 per page
- No authentication required (public catalogue)

**Contact form**
- Saves inquiry to DB; sends auto-reply to customer, then staff notification
- If auto-reply fails, staff notification is suppressed (customer would have no confirmation)
- Product pre-selected when arriving from a product detail page (`?product=<slug>`)
- Rate-limited: 10 POST/IP/hour; custom branded 429 page

**Image processing**
- 10 MB size limit; resizes to max 1200 px width on upload via Pillow
- Applies to products, categories, news posts, and hero slides
- `img.format` captured before resize (Pillow clears it post-resize)

**SEO**
- Editable `meta_title` / `meta_description` on every product and news post
- `sitemap.xml` with three sitemaps (static pages, products, news posts) including `lastmod`
- `robots.txt`, `favicon.ico` redirect, SVG + 192 px + 48 px + Apple touch favicons
- Open Graph tags (`og:type`, `og:url`, `og:title`, `og:description`, `og:site_name`) on every page
- JSON-LD `Organization` schema on the home page
- GA4 (conditional on `GA_TRACKING_ID`); canonical URL in every template

**Admin**
- Jazzmin green theme; custom icons per model; `save_on_top = True`
- `TagsWidget` — interactive pill UI for comma-separated fields (alternative names, available forms)
- `SpecsTableWidget` — editable table UI that serialises to pipe-separated text
- Image preview thumbnails on Category and Product list views
- `SiteSettings` singleton (phone, email, address, map embed, social links) with 5-minute cache
- `HeroSlide` model — admin-managed homepage carousel with order control

**Management commands**
- `fetch_product_images` — queries Wikimedia Commons for freely-licensed product images; scoring algorithm rejects SVGs, diagrams (aspect ratio), molecular structure images (keyword list), and low-resolution files
- `clean_product_text` — normalises scraper artefacts (non-breaking spaces, etc.) across all product text fields; supports `--dry-run`

---

## Infrastructure

```
Browser
  └── CloudFront CDN  (PriceClass_200 — US, Europe, Asia, Middle East, Africa)
        ├── EC2 t4g.micro  ap-southeast-1a
        │     ├── nginx       (reverse proxy, SSL termination)
        │     ├── gunicorn    (WSGI, systemd-managed)
        │     ├── Django 6
        │     └── PostgreSQL  (same instance)
        └── S3  gfi-website-media
              ├── static/     (collected static files)
              └── media/      (uploaded media)
```

CloudFront distribution `E29UCPY78B4EJQ` is provisioned and deployed. Setting `AWS_CLOUDFRONT_DOMAIN` on EC2 activates it with no redeploy.

---

## Key Engineering Decisions

**Both static and media files served via S3 + CloudFront**
All file serving routes through a single CDN origin. Static files are pushed to S3 on each deploy via `collectstatic`; media files land there on upload. nginx handles only the Django application — no file serving at the app layer.

**PostgreSQL on the same EC2 instance as the app**
Eliminates the ~$15–30/month RDS cost and removes a network hop between app and database. For a brochure site, brief downtime has low business impact; data is backed up nightly.

**`deploy/aws` as a separate deploy branch**
GitHub Actions only deploys when code is pushed to `deploy/aws`, not `main`. Development work can accumulate on `main` without every merge triggering a production push — deploys are explicit and intentional.

**Stored `SearchVector` with weighted fields and a GIN index**
Annotating a vector on every query rescans all rows. A stored field updated by a `post_save` signal hits the GIN index directly. Field weights surface exact identifiers (CAS numbers, E-numbers) above prose matches — the dominant search pattern for B2B food-additive buyers.

**Two-tier partial swap instead of a full-page SPA or HTMX**
The product catalogue needs two distinct interaction speeds: filter/category changes (full section swap with fade, `pushState`) vs. live search (grid-only update, no focus loss, 350 ms debounce). A single fetch-and-replace strategy couldn't serve both without layout flash or focus interruption. The result is ~240 lines of vanilla JS with no framework dependency.

**Rate limiting at the view layer, not at nginx**
`django-ratelimit` ties the limit to Django's request context, which works correctly behind a load balancer with `X-Forwarded-For`, can be unit-tested without standing up nginx, and produces a proper Django 429 response with a branded error page.

**Auto-reply gates staff notification**
On a valid inquiry, the auto-reply is sent first. If it fails (SMTP error), staff notification is suppressed — preventing staff from responding to a customer who never received a confirmation. The logic is: send auto-reply → on success, send staff notification; on failure, log and stop.

---

## Project Structure

```
config/
  settings/
    base.py          Shared settings (all apps, email, rate limiting, REST framework)
    development.py   SQLite fallback, debug toolbar, browser reload
    production.py    S3 backends, security headers, HSTS
apps/
  products/          Catalogue — models, views, signals, admin widgets, REST API
    api/             DRF viewsets, serializers, filter classes
    management/      fetch_product_images, clean_product_text
    templatetags/    parse_specs filter (pipe-separated → HTML table)
  news/              Blog/announcements (Summernote rich text)
  pages/             Home, About, Services; SiteSettings singleton; HeroSlide; sitemaps
  contact/           Inquiry form — DB write, dual email, rate limiting
  utils/             Image processing (images.py), S3 storage backends (storage.py)
templates/           Base layout, per-app templates, partials, error pages (400/403/404/429/500)
static/
  css/               tokens.css → components/ → main.css
  js/                products.js (partial swap), navbar.js, hero.js, ui.js
```

---

## REST API

```
GET /api/products/          List products  (paginated, 20/page)
GET /api/products/<slug>/   Product detail
GET /api/categories/        List categories  (includes product_count)

?search=          Full-text search (name, CAS, E-number, alt names, description)
?category=        Filter by category slug
?certification=   Filter by certification slug
?ordering=        name | -name | created_at
```

---

## Local Setup

```bash
git clone https://github.com/nufelroknidev/gfi-website && cd gfi-website

pip install poetry
poetry install

cp .env.example .env   # fill in values

poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

Admin at `/admin/`. Default settings module: `config.settings.development` (SQLite, console email, debug toolbar).

## Tests

```bash
poetry run python manage.py test apps.pages apps.products apps.contact apps.news
```

36 tests covering model validation, form submission (DB write + email), URL resolution, admin access control, rate limiting (429), and DRF API filters. PostgreSQL-specific features (FTS, signals) are skipped automatically on SQLite.

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3 / CloudFront credentials |
| `AWS_STORAGE_BUCKET_NAME` | `gfi-website-media` |
| `AWS_S3_REGION_NAME` | `ap-southeast-1` |
| `AWS_CLOUDFRONT_DOMAIN` | Set to activate CDN — omit to serve from S3 directly |
| `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP (Brevo) |
| `EMAIL_PORT` | SMTP port (default: 587) |
| `DEFAULT_FROM_EMAIL` | Sender address for all outbound email |
| `CONTACT_EMAIL` | Staff inbox that receives inquiry notifications |
| `GA_TRACKING_ID` | Google Analytics 4 measurement ID |
| `CANONICAL_DOMAIN` | Canonical URL injected into all templates |

---

## CI/CD

Push to `deploy/aws` →
1. GitHub Actions runs the full test suite (SQLite, no AWS credentials needed)
2. On pass, SSHes into EC2 and runs: `git pull` → `poetry install --only main` → `migrate` → `collectstatic` → `systemctl restart gunicorn`

Deploy is blocked if any test fails.

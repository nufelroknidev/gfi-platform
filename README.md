# GFI — General Food Industry Co., Ltd.

B2B marketing website for a Thai food additives importer/distributor. The site presents the product catalogue across six languages, publishes industry news, and funnels inquiries through a contact form. No e-commerce.

---

## Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.13 / Django |
| Dependencies | Poetry |
| Frontend | Django templates + Bootstrap 5 |
| Database | PostgreSQL (self-hosted on EC2) |
| Media storage | AWS S3 (`django-storages` / `S3Boto3Storage`) |
| Admin UI | `django-jazzmin` |
| i18n | Django's built-in translation framework |

---

## Infrastructure

- **EC2 `t4g.micro`** — `ap-southeast-1a` (Singapore). Nginx as reverse proxy, Gunicorn as WSGI server.
- **PostgreSQL** — runs on the same EC2 instance.
- **S3 bucket `gfi-website-media`** — uploaded media only. Static files are collected locally and served by Nginx.
- **CI/CD** — GitHub Actions deploys via SSH on push to `deploy/aws`.

---

## Project structure

```
config/
  settings/
    base.py        Shared settings
    production.py  S3 media backend, security flags
apps/
  products/        Catalogue — categories, products, SEO fields
  news/            News and announcements
  pages/           Home, About, Services, Contact
  contact/         Inquiry form — saves to DB, sends email
templates/         Base layout, per-app templates, partials
static/css/        tokens.css → main.css → base.css
locale/            Translation files for 6 languages
```

---

## Key decisions

**EC2 over Beanstalk or App Runner**
Full control, lower cost, no managed-platform overhead for a site at this traffic scale. The tradeoff is manual server administration.

**PostgreSQL on the same instance as the app**
Avoids RDS cost and eliminates network round-trips between app and database. Acceptable risk for a brochure site — brief downtime has low business impact and data is backed up.

**S3 for media, not for static files**
Static files are build artefacts that never change at runtime — `collectstatic` to local disk is sufficient. Media files are user-uploaded and grow over time, so S3 handles durability and scale without touching the server.

**`deploy/aws` branch as the deploy gate**
GitHub Actions only deploys when code lands on `deploy/aws`, not `main`. This lets development continue on `main` without every merge triggering a production push. Deploys are intentional.

**i18n from day one**
GFI's customers span Thailand, France, Spain, the Arab world, and China. Adding translation support to an existing Django project mid-build is expensive — templates need auditing and string extraction misses things. `{% trans %}` from the first template meant no rework.

**No inline styles**
All CSS lives in `static/css/`. Templates hold only class names. Enforced from the start so the markup stays readable and design changes stay in one place.

---

## CI/CD

Push to `deploy/aws` →
1. GitHub Actions runs the test suite
2. On pass, SSHes into EC2 and runs `git pull`, `poetry install`, `migrate`, `collectstatic`, `systemctl restart gunicorn`

Deploy is blocked if tests fail.

---

## Local setup

```bash
git clone <repo-url> && cd gfi-website

python -m venv venv && source venv/bin/activate
pip install poetry && poetry install

cp .env.example .env   # fill in values

python manage.py migrate
python manage.py createsuperuser
python manage.py compilemessages
python manage.py runserver
```

Admin at `/en/admin/`.

---

## Environment variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3 credentials |
| `AWS_STORAGE_BUCKET_NAME` | `gfi-website-media` |
| `AWS_S3_REGION_NAME` | `ap-southeast-1` |
| `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP for inquiry emails |
| `GA_TRACKING_ID` | Google Analytics 4 measurement ID |

---

## Internationalisation

English, Thai, French, Spanish, Arabic, Simplified Chinese. Every template string uses `{% trans %}` or `{% blocktrans %}`. Arabic triggers RTL via `dir="rtl"` on `<html>`. Language switcher in the navbar.

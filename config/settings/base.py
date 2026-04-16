from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# base.py lives at config/settings/base.py — three .parent calls to reach repo root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CANONICAL_DOMAIN = env('CANONICAL_DOMAIN', default='https://www.generalfoodindustry.com')

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django_summernote',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # Local apps
    'apps.pages',
    'apps.products',
    'apps.news',
    'apps.contact',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.pages.context_processors.site_globals',
            ],
            'libraries': {
                'product_tags': 'apps.products.templatetags.product_tags',
            },
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@gfi.example.com')
CONTACT_EMAIL = env('CONTACT_EMAIL', default='info@gfi.example.com')

# ── Analytics ─────────────────────────────────────────────────────────────────
GA_TRACKING_ID = env('GA_TRACKING_ID', default='')

# ── Summernote (rich text editor) ─────────────────────────────────────────
SUMMERNOTE_CONFIG = {
    "summernote": {
        "width": "100%",
        "height": "400px",
        "toolbar": [
            ["style", ["bold", "italic", "underline", "clear"]],
            ["para", ["ul", "ol", "paragraph"]],
            ["insert", ["link", "picture", "hr"]],
            ["view", ["fullscreen", "codeview"]],
        ],
        "codemirror": {
            "mode": "htmlmixed",
            "lineNumbers": True,
        },
    },
    "attachment_upload_to": "news/attachments/",
    "attachment_filesize_limit": 5 * 1024 * 1024,  # 5 MB
}

# ── Django Jazzmin (admin UI) ──────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "GFI Admin",
    "site_header": "General Food Industry",
    "site_brand": "GFI",
    "welcome_sign": "Welcome to the GFI Admin Panel",
    "copyright": "General Food Industry Co., Ltd.",

    # Top navigation links
    "topmenu_links": [
        {"name": "View Website", "url": "/", "new_window": True},
    ],

    # Hide Groups — staff only need to manage Users
    "hide_models": ["auth.group"],

    # Custom icons for each app/model in the sidebar
    "icons": {
        "pages.sitesettings": "fas fa-sliders-h",
        "products.category": "fas fa-tags",
        "products.certification": "fas fa-certificate",
        "products.application": "fas fa-industry",
        "products.product": "fas fa-box-open",
        "news.post": "fas fa-newspaper",
        "contact.inquiry": "fas fa-envelope",
        "auth.user": "fas fa-user",
    },

    # Disable the runtime UI builder — keeps brand theming locked in
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "brand_colour": "navbar-success",
    "accent": "accent-olive",
    "navbar": "navbar-success navbar-dark",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_child_indent": True,
}

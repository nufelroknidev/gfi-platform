from django.conf import settings
from django.core.cache import cache

from .models import SiteSettings

_SITE_SETTINGS_CACHE_KEY = "site_settings"
_SITE_SETTINGS_TTL = 300  # seconds — invalidated immediately on admin save


def _get_site_settings():
    obj = cache.get(_SITE_SETTINGS_CACHE_KEY)
    if obj is None:
        obj = SiteSettings.load()
        cache.set(_SITE_SETTINGS_CACHE_KEY, obj, _SITE_SETTINGS_TTL)
    return obj


def site_globals(request):
    canonical_domain = getattr(settings, 'CANONICAL_DOMAIN', 'https://www.generalfoodindustry.com')
    return {
        'GA_TRACKING_ID': getattr(settings, 'GA_TRACKING_ID', ''),
        'SITE_SETTINGS': _get_site_settings(),
        'CANONICAL_DOMAIN': canonical_domain,
        'CANONICAL_URL': f"{canonical_domain}{request.path}",
    }

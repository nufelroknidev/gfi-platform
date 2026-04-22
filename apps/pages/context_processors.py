from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language

from .models import SiteSettings

# Language data lives here so templates can loop over it rather than
# hardcoding one block per language. Flag codes follow the flag-icons
# library (ISO 3166-1 alpha-2); Arabic uses Saudi Arabia 'sa'.
# Keep this list in sync with settings.LANGUAGES when adding/removing languages.
SUPPORTED_LANGUAGES = [
    {'code': 'en',      'flag': 'gb', 'label': 'English'},
    {'code': 'th',      'flag': 'th', 'label': 'ภาษาไทย'},
    {'code': 'fr',      'flag': 'fr', 'label': 'Français'},
    {'code': 'es',      'flag': 'es', 'label': 'Español'},
    {'code': 'ar',      'flag': 'sa', 'label': 'العربية'},
    {'code': 'zh-hans', 'flag': 'cn', 'label': '中文'},
]

_FALLBACK_LANGUAGE = {'code': '', 'flag': None, 'label': 'Language'}

_SITE_SETTINGS_CACHE_KEY = "site_settings"
_SITE_SETTINGS_TTL = 300  # seconds — invalidated immediately on admin save


def _get_site_settings():
    obj = cache.get(_SITE_SETTINGS_CACHE_KEY)
    if obj is None:
        obj = SiteSettings.load()
        cache.set(_SITE_SETTINGS_CACHE_KEY, obj, _SITE_SETTINGS_TTL)
    return obj


def _bare_path(path, lang_code):
    """Strip non-default language prefix from path, returning the English-canonical form."""
    if lang_code and lang_code != settings.LANGUAGE_CODE:
        prefix = f'/{lang_code}/'
        if path.startswith(prefix):
            return '/' + path[len(prefix):]
    return path


def site_globals(request):
    lang_code = get_language() or settings.LANGUAGE_CODE
    current_lang = next(
        (l for l in SUPPORTED_LANGUAGES if l['code'] == lang_code),
        _FALLBACK_LANGUAGE,
    )

    canonical_domain = getattr(settings, 'CANONICAL_DOMAIN', 'https://www.generalfoodindustry.com')
    path = _bare_path(request.path, lang_code)
    english_url = f"{canonical_domain}{path}"

    if lang_code == settings.LANGUAGE_CODE:
        canonical_url = english_url
    else:
        canonical_url = f"{canonical_domain}/{lang_code}{path}"

    hreflang_urls = [
        {
            'lang': lang['code'],
            'url': english_url if lang['code'] == settings.LANGUAGE_CODE
                   else f"{canonical_domain}/{lang['code']}{path}",
        }
        for lang in SUPPORTED_LANGUAGES
    ]

    return {
        'GA_TRACKING_ID': getattr(settings, 'GA_TRACKING_ID', ''),
        'SUPPORTED_LANGUAGES': SUPPORTED_LANGUAGES,
        'LANGUAGE_CODE': lang_code,
        'CURRENT_LANGUAGE': current_lang,
        'SITE_SETTINGS': _get_site_settings(),
        'CANONICAL_DOMAIN': canonical_domain,
        'CANONICAL_URL': canonical_url,
        'CANONICAL_URL_EN': english_url,
        'HREFLANG_URLS': hreflang_urls,
    }

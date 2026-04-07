from django.conf import settings
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


def site_globals(request):
    lang_code = get_language() or settings.LANGUAGE_CODE
    current_lang = next(
        (l for l in SUPPORTED_LANGUAGES if l['code'] == lang_code),
        _FALLBACK_LANGUAGE,
    )
    return {
        'GA_TRACKING_ID':      getattr(settings, 'GA_TRACKING_ID', ''),
        'SUPPORTED_LANGUAGES': SUPPORTED_LANGUAGES,
        'LANGUAGE_CODE':       lang_code,
        'CURRENT_LANGUAGE':    current_lang,
        'SITE_SETTINGS':       SiteSettings.load(),
    }

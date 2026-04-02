from django.conf import settings


def ga_tracking(request):
    return {'GA_TRACKING_ID': getattr(settings, 'GA_TRACKING_ID', '')}

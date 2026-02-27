from django.conf import settings as django_settings
from .models import SeoSettings


def seo_settings(request):
    biz = SeoSettings.load()
    return {
        'seo_settings': biz,
        'SITE_URL': getattr(django_settings, 'SITE_URL', ''),
    }

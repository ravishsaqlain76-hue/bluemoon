from django.conf import settings as django_settings
from .models import SeoSettings


def seo_settings(request):
    biz = SeoSettings.load()
    ctx = {
        'seo_settings': biz,
        'SITE_URL': getattr(django_settings, 'SITE_URL', ''),
    }

    # Add user role for easy template access
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            ctx['user_role'] = request.user.profile.role
        except Exception:
            ctx['user_role'] = 'guest'
    else:
        ctx['user_role'] = None

    return ctx

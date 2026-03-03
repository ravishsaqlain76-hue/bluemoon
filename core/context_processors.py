from django.conf import settings as django_settings
from django.urls import reverse
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

    # Property context from middleware
    gh = getattr(request, 'guest_house', None)
    if gh:
        ctx['guest_house'] = gh
        ctx['business'] = gh
        slug = gh.slug
        ctx['nav_home_url'] = reverse('property_home', kwargs={'property_slug': slug})
        ctx['nav_rooms_url'] = reverse('rooms:room_list', kwargs={'property_slug': slug})
        ctx['nav_about_url'] = reverse('property_about', kwargs={'property_slug': slug})
        ctx['nav_contact_url'] = reverse('property_contact', kwargs={'property_slug': slug})
        ctx['nav_location_url'] = reverse('property_location_landing', kwargs={'property_slug': slug})
        ctx['nav_location_islamabad_url'] = reverse('property_location_islamabad', kwargs={'property_slug': slug})
        ctx['nav_location_faisal_url'] = reverse('property_location_near_faisal_mosque', kwargs={'property_slug': slug})
        ctx['nav_booking_url'] = reverse('property_booking_landing', kwargs={'property_slug': slug})
    else:
        ctx['nav_home_url'] = reverse('home')
        ctx['nav_rooms_url'] = reverse('home')
        ctx['nav_about_url'] = reverse('home')
        ctx['nav_contact_url'] = reverse('home')
        ctx['nav_location_url'] = reverse('home')
        ctx['nav_location_islamabad_url'] = reverse('home')
        ctx['nav_location_faisal_url'] = reverse('home')
        ctx['nav_booking_url'] = reverse('home')

    return ctx

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.db.models import Avg, Count
from rooms.models import Room
from .models import SeoSettings, PageSeo, Testimonial, FAQ, NearbyAttraction


def _get_page_seo(page_key):
    try:
        return PageSeo.objects.get(page=page_key)
    except PageSeo.DoesNotExist:
        return None


def _get_review_aggregate():
    """Return aggregate rating data for schema markup."""
    agg = Testimonial.objects.filter(is_active=True).aggregate(
        avg=Avg('rating'), count=Count('id')
    )
    return {
        'review_avg': round(agg['avg'], 1) if agg['avg'] else 0,
        'review_count': agg['count'] or 0,
    }


def home(request):
    rooms = Room.objects.filter(status='available')[:6]
    featured_rooms = Room.objects.filter(featured=True, status='available')[:4]
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    faqs = FAQ.objects.filter(is_active=True)[:8]
    attractions = NearbyAttraction.objects.all()[:8]
    settings = SeoSettings.load()
    context = {
        'rooms': rooms,
        'featured_rooms': featured_rooms,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
        'page_seo': _get_page_seo('home'),
        'business': settings,
    }
    context.update(_get_review_aggregate())
    return render(request, 'landing.html', context)


def about(request):
    testimonials = Testimonial.objects.filter(is_active=True)[:4]
    context = {
        'page_seo': _get_page_seo('about'),
        'testimonials': testimonials,
    }
    context.update(_get_review_aggregate())
    return render(request, 'about.html', context)


def contact(request):
    settings = SeoSettings.load()
    if request.method == 'POST':
        name = request.POST.get('name', '')
        messages.success(request, f'Thanks {name}! Your message has been received.')
        return redirect('contact')
    return render(request, 'contact.html', {
        'page_seo': _get_page_seo('contact'),
        'business': settings,
    })


def location_landing(request):
    rooms = Room.objects.filter(status='available')[:6]
    testimonials = Testimonial.objects.filter(is_active=True)[:4]
    faqs = FAQ.objects.filter(is_active=True, category='location')
    attractions = NearbyAttraction.objects.all()
    settings = SeoSettings.load()
    context = {
        'rooms': rooms,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
        'page_seo': _get_page_seo('location'),
        'business': settings,
    }
    context.update(_get_review_aggregate())
    return render(request, 'location.html', context)


def location_islamabad(request):
    """Broader location page targeting 'guest house in islamabad'."""
    rooms = Room.objects.filter(status='available')[:6]
    testimonials = Testimonial.objects.filter(is_active=True)[:4]
    faqs = FAQ.objects.filter(is_active=True)[:6]
    attractions = NearbyAttraction.objects.all()
    settings = SeoSettings.load()
    context = {
        'rooms': rooms,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
        'page_seo': _get_page_seo('location_islamabad'),
        'business': settings,
    }
    context.update(_get_review_aggregate())
    return render(request, 'location_islamabad.html', context)


def location_near_faisal_mosque(request):
    """Location page targeting 'guest house near faisal mosque'."""
    rooms = Room.objects.filter(status='available')[:6]
    testimonials = Testimonial.objects.filter(is_active=True)[:4]
    settings = SeoSettings.load()
    context = {
        'rooms': rooms,
        'testimonials': testimonials,
        'page_seo': _get_page_seo('location_near_faisal_mosque'),
        'business': settings,
    }
    context.update(_get_review_aggregate())
    return render(request, 'location_faisal_mosque.html', context)


@cache_page(60 * 60 * 24)
def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        'Disallow: /admin/',
        'Disallow: /accounts/dashboard/',
        'Disallow: /accounts/profile/',
        'Disallow: /bookings/',
        '',
        f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')

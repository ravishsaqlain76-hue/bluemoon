from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.db.models import Avg, Count
from rooms.models import Room
from .models import Property, SeoSettings, PageSeo, Testimonial, FAQ, NearbyAttraction


def _get_page_seo(page_key, guest_house=None):
    try:
        if guest_house:
            return PageSeo.objects.get(page=page_key, guest_house=guest_house)
        return PageSeo.objects.filter(page=page_key).first()
    except PageSeo.DoesNotExist:
        return None


def _get_review_aggregate(guest_house=None):
    """Return aggregate rating data for schema markup."""
    qs = Testimonial.objects.filter(is_active=True)
    if guest_house:
        qs = qs.filter(guest_house=guest_house)
    agg = qs.aggregate(avg=Avg('rating'), count=Count('id'))
    return {
        'review_avg': round(agg['avg'], 1) if agg['avg'] else 0,
        'review_count': agg['count'] or 0,
    }


def landing_page(request):
    """Root page: if one property, redirect to it. Otherwise show selector."""
    properties = Property.objects.filter(is_active=True)
    if properties.count() == 1:
        return redirect(properties.first().get_absolute_url())
    return render(request, 'property_selector.html', {'properties': properties})


def property_home(request, property_slug):
    gh = request.guest_house
    rooms = Room.objects.filter(guest_house=gh, status='available')[:6]
    featured_rooms = Room.objects.filter(guest_house=gh, featured=True, status='available')[:4]
    testimonials = Testimonial.objects.filter(guest_house=gh, is_active=True)[:6]
    faqs = FAQ.objects.filter(guest_house=gh, is_active=True)[:8]
    attractions = NearbyAttraction.objects.filter(guest_house=gh)[:8]
    context = {
        'rooms': rooms,
        'featured_rooms': featured_rooms,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
        'page_seo': _get_page_seo('home', gh),
        'business': gh,
        'guest_house': gh,
    }
    context.update(_get_review_aggregate(gh))
    return render(request, 'landing.html', context)


def property_about(request, property_slug):
    gh = request.guest_house
    testimonials = Testimonial.objects.filter(guest_house=gh, is_active=True)[:4]
    context = {
        'page_seo': _get_page_seo('about', gh),
        'testimonials': testimonials,
        'guest_house': gh,
        'business': gh,
    }
    context.update(_get_review_aggregate(gh))
    return render(request, 'about.html', context)


def property_contact(request, property_slug):
    gh = request.guest_house
    if request.method == 'POST':
        name = request.POST.get('name', '')
        messages.success(request, f'Thanks {name}! Your message has been received.')
        return redirect('property_contact', property_slug=property_slug)
    return render(request, 'contact.html', {
        'page_seo': _get_page_seo('contact', gh),
        'business': gh,
        'guest_house': gh,
    })


def property_location_landing(request, property_slug):
    gh = request.guest_house
    rooms = Room.objects.filter(guest_house=gh, status='available')[:6]
    testimonials = Testimonial.objects.filter(guest_house=gh, is_active=True)[:4]
    faqs = FAQ.objects.filter(guest_house=gh, is_active=True, category='location')
    attractions = NearbyAttraction.objects.filter(guest_house=gh)
    context = {
        'rooms': rooms,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
        'page_seo': _get_page_seo('location', gh),
        'business': gh,
        'guest_house': gh,
    }
    context.update(_get_review_aggregate(gh))
    return render(request, 'location.html', context)


def property_location_islamabad(request, property_slug):
    gh = request.guest_house
    rooms = Room.objects.filter(guest_house=gh, status='available')[:6]
    testimonials = Testimonial.objects.filter(guest_house=gh, is_active=True)[:4]
    faqs = FAQ.objects.filter(guest_house=gh, is_active=True)[:6]
    attractions = NearbyAttraction.objects.filter(guest_house=gh)
    context = {
        'rooms': rooms,
        'testimonials': testimonials,
        'faqs': faqs,
        'attractions': attractions,
        'page_seo': _get_page_seo('location_islamabad', gh),
        'business': gh,
        'guest_house': gh,
    }
    context.update(_get_review_aggregate(gh))
    return render(request, 'location_islamabad.html', context)


def property_location_near_faisal_mosque(request, property_slug):
    gh = request.guest_house
    rooms = Room.objects.filter(guest_house=gh, status='available')[:6]
    testimonials = Testimonial.objects.filter(guest_house=gh, is_active=True)[:4]
    context = {
        'rooms': rooms,
        'testimonials': testimonials,
        'page_seo': _get_page_seo('location_near_faisal_mosque', gh),
        'business': gh,
        'guest_house': gh,
    }
    context.update(_get_review_aggregate(gh))
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

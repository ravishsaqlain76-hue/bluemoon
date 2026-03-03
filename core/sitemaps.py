from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from rooms.models import Room
from core.models import Property


class StaticSitemap(Sitemap):
    changefreq = 'weekly'

    def items(self):
        """Generate static pages for each active property."""
        pages = []
        for prop in Property.objects.filter(is_active=True):
            slug = prop.slug
            pages.append(('property_home', slug, 1.0))
            pages.append(('property_about', slug, 0.8))
            pages.append(('property_contact', slug, 0.8))
            pages.append(('property_location_landing', slug, 0.9))
            pages.append(('property_location_islamabad', slug, 0.9))
            pages.append(('property_location_near_faisal_mosque', slug, 0.9))
        # Root page
        pages.append(('home', None, 0.5))
        return pages

    def location(self, item):
        name, slug, _ = item
        if slug:
            return reverse(name, kwargs={'property_slug': slug})
        return reverse(name)

    def priority(self, item):
        _, _, prio = item
        return prio


class RoomSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Room.objects.filter(status='available').select_related('guest_house')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        if obj.guest_house:
            return reverse('rooms:room_detail', kwargs={'property_slug': obj.guest_house.slug, 'slug': obj.slug})
        return f'/rooms/{obj.slug}/'


class RoomListSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return Property.objects.filter(is_active=True)

    def location(self, prop):
        return reverse('rooms:room_list', kwargs={'property_slug': prop.slug})

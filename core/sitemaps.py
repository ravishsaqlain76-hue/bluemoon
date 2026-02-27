from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from rooms.models import Room


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home', 'about', 'contact',
            'location_landing', 'location_islamabad', 'location_near_faisal_mosque',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'home':
            return 1.0
        if item.startswith('location'):
            return 0.9
        return 0.8


class RoomSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Room.objects.filter(status='available')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('rooms:room_detail', args=[obj.slug])


class RoomListSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return ['rooms:room_list']

    def location(self, item):
        return reverse(item)

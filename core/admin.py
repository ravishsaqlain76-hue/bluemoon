from django.contrib import admin
from .models import SeoSettings, PageSeo, Testimonial, FAQ, NearbyAttraction


@admin.register(SeoSettings)
class SeoSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Site Defaults', {
            'fields': ['site_name', 'default_meta_title', 'default_meta_description', 'default_keywords', 'og_image'],
        }),
        ('Business Information (JSON-LD Schema)', {
            'fields': ['business_name', 'street_address', 'locality', 'region', 'postal_code', 'country', 'phone', 'email'],
        }),
        ('Location', {
            'fields': ['latitude', 'longitude', 'google_maps_embed_url'],
        }),
        ('Display & Pricing', {
            'fields': ['currency_symbol', 'price_range', 'check_in_time', 'check_out_time'],
        }),
    ]

    def has_add_permission(self, request):
        return not SeoSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageSeo)
class PageSeoAdmin(admin.ModelAdmin):
    list_display = ['page', 'meta_title', 'meta_description']
    list_editable = ['meta_title', 'meta_description']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'location', 'room_type', 'date', 'is_active']
    list_filter = ['rating', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name', 'text']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['question', 'answer']


@admin.register(NearbyAttraction)
class NearbyAttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'distance', 'order']
    list_filter = ['category']
    list_editable = ['order']
    search_fields = ['name']

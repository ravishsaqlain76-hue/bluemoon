from django.contrib import admin
from .models import Room, RoomImage


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'guest_house', 'room_type', 'price_per_night', 'capacity', 'status', 'featured']
    list_filter = ['guest_house', 'room_type', 'status', 'featured']
    list_editable = ['status', 'price_per_night', 'featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RoomImageInline]
    fieldsets = [
        (None, {
            'fields': ['guest_house', 'name', 'slug', 'room_type', 'description', 'price_per_night', 'capacity', 'status', 'amenities', 'featured', 'bed_type', 'room_size'],
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ['meta_title', 'meta_description'],
        }),
    ]


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room', 'caption', 'is_primary']
    list_filter = ['is_primary', 'room__guest_house']

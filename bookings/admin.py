from django.contrib import admin
from .models import Booking


@admin.action(description='Approve selected bookings')
def approve_bookings(modeladmin, request, queryset):
    queryset.filter(status='pending').update(status='confirmed')


@admin.action(description='Cancel selected bookings')
def cancel_bookings(modeladmin, request, queryset):
    queryset.filter(status__in=['pending', 'confirmed']).update(status='cancelled')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'get_guest_name', 'get_guest_email', 'get_guest_phone', 'room', 'check_in', 'check_out', 'total_price', 'status', 'get_booking_type', 'created_at']
    list_filter = ['status', 'payment_method', 'room', 'created_at']
    search_fields = ['booking_reference', 'user__username', 'room__name', 'guest_name', 'guest_email', 'guest_phone']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    actions = [approve_bookings, cancel_bookings]
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Booking Info', {
            'fields': ('booking_reference', 'room', 'status', 'payment_method'),
        }),
        ('Guest Info', {
            'fields': ('user', 'guest_name', 'guest_email', 'guest_phone'),
        }),
        ('Stay Details', {
            'fields': ('check_in', 'check_out', 'guests', 'total_price', 'special_requests'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description='Guest')
    def get_guest_name(self, obj):
        return obj.guest_display_name

    @admin.display(description='Email')
    def get_guest_email(self, obj):
        return obj.guest_contact_email

    @admin.display(description='Phone')
    def get_guest_phone(self, obj):
        if obj.user and hasattr(obj.user, 'profile'):
            return obj.user.profile.phone or obj.guest_phone
        return obj.guest_phone

    @admin.display(description='Type', boolean=True)
    def get_booking_type(self, obj):
        return not obj.is_guest_booking

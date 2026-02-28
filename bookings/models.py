import uuid
from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    PAYMENT_CHOICES = [
        ('check_in', 'Pay at Check-in'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    guest_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_reference = models.CharField(max_length=12, unique=True, editable=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='check_in')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.room.name}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    @property
    def num_nights(self):
        return (self.check_out - self.check_in).days

    @property
    def guest_display_name(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.guest_name

    @property
    def guest_contact_email(self):
        if self.user:
            return self.user.email
        return self.guest_email

    @property
    def is_guest_booking(self):
        return self.user is None

    @classmethod
    def has_overlap(cls, room, check_in, check_out, exclude_pk=None):
        """Check if any active booking overlaps the given date range for this room."""
        qs = cls.objects.filter(
            room=room,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

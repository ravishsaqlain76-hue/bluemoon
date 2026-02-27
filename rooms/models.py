from django.db import models
from django.utils.text import slugify


class Room(models.Model):
    ROOM_TYPES = [
        ('standard', 'Standard'),
        ('deluxe', 'Deluxe'),
        ('suite', 'Suite'),
        ('family', 'Family'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    amenities = models.TextField(blank=True, help_text='Comma-separated list of amenities')
    featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=70, blank=True, help_text='SEO title (auto-generated if blank)')
    meta_description = models.CharField(max_length=160, blank=True, help_text='SEO description (auto-generated if blank)')
    bed_type = models.CharField(max_length=50, blank=True, help_text='e.g. King, Twin, Queen')
    room_size = models.CharField(max_length=30, blank=True, help_text='e.g. 25 sqm')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_meta_title(self):
        if self.meta_title:
            return self.meta_title
        return f"{self.name} | Guest House Room in F-6/2 Islamabad | Blue Moon Residency"

    def get_meta_description(self):
        if self.meta_description:
            return self.meta_description
        return f"Book {self.name} at Blue Moon Residency, F-6/2 Islamabad. {self.get_room_type_display()} room for {self.capacity} guests at PKR {self.price_per_night:,.0f}/night. Wi-Fi, AC, and more."

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.room.name}"

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class SeoSettings(models.Model):
    """Singleton model for site-wide SEO settings editable from admin."""
    site_name = models.CharField(max_length=100, default='Blue Moon Residency')
    default_meta_title = models.CharField(
        max_length=70,
        default='Blue Moon Residency | Best Guest House in F6/2 Islamabad',
        help_text='Default title for pages without a specific title (max 70 chars)',
    )
    default_meta_description = models.TextField(
        max_length=160,
        default='Blue Moon Residency is a top-rated guest house in F-6/2, Islamabad. Comfortable rooms, great service, and prime location near Faisal Mosque. Book now!',
        help_text='Default meta description (max 160 chars)',
    )
    default_keywords = models.TextField(
        blank=True,
        default='guest house islamabad, guest house F6/2, blue moon residency, hotel islamabad, guest house near me, accommodation islamabad, F-6 islamabad hotel',
        help_text='Comma-separated keywords',
    )
    business_name = models.CharField(max_length=200, default='Blue Moon Residency')
    street_address = models.CharField(max_length=300, default='House # 2-A, Justice Abdul Rasheed Road')
    locality = models.CharField(max_length=100, default='Islamabad')
    region = models.CharField(max_length=100, default='Islamabad Capital Territory')
    postal_code = models.CharField(max_length=20, default='44000')
    country = models.CharField(max_length=5, default='PK')
    phone = models.CharField(max_length=30, blank=True, default='+92-XXX-XXXXXXX')
    phone2 = models.CharField(max_length=30, blank=True, default='', help_text='Second contact number (optional)')
    email = models.EmailField(blank=True, default='info@bluemoonresidency.com')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, default=33.7294000)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, default=73.0931000)
    google_maps_embed_url = models.URLField(
        blank=True,
        max_length=500,
        default='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3318.8!2d73.093!3d33.729!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMzPCsDQzJzQ1LjgiTiA3M8KwMDUnMzUuMiJF!5e0!3m2!1sen!2spk!4v1',
        help_text='Google Maps embed URL for iframe',
    )
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True, help_text='Default Open Graph image (1200x630 recommended)')
    currency_symbol = models.CharField(max_length=10, default='PKR', help_text='Currency symbol shown on site (PKR, Rs., etc.)')
    price_range = models.CharField(max_length=20, default='PKR 5,000 - 25,000', help_text='Price range for schema markup')
    check_in_time = models.CharField(max_length=10, default='14:00', help_text='Check-in time (24h format)')
    check_out_time = models.CharField(max_length=10, default='12:00', help_text='Check-out time (24h format)')
    booking_com_url = models.URLField(
        max_length=500, blank=True, default='',
        help_text='Booking.com listing URL. If set, "Book Now" buttons will link here instead of the internal booking system. Leave empty to use internal bookings.',
    )

    class Meta:
        verbose_name = 'SEO Settings'
        verbose_name_plural = 'SEO Settings'

    def __str__(self):
        return 'SEO Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PageSeo(models.Model):
    """Per-page SEO overrides editable from admin."""
    PAGE_CHOICES = [
        ('home', 'Home'),
        ('about', 'About'),
        ('contact', 'Contact'),
        ('rooms', 'Rooms'),
        ('location', 'Guest House in F6/2 Islamabad'),
        ('location_islamabad', 'Guest House in Islamabad'),
        ('location_near_faisal_mosque', 'Guest House Near Faisal Mosque'),
    ]

    page = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    meta_title = models.CharField(max_length=70, blank=True, help_text='Page title (max 70 chars)')
    meta_description = models.TextField(max_length=160, blank=True, help_text='Meta description (max 160 chars)')
    keywords = models.TextField(blank=True, help_text='Comma-separated keywords')

    class Meta:
        verbose_name = 'Page SEO'
        verbose_name_plural = 'Page SEO'

    def __str__(self):
        return f"SEO: {self.get_page_display()}"


class Testimonial(models.Model):
    """Guest reviews/testimonials displayed on site and used for AggregateRating schema."""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, help_text='e.g. Lahore, Pakistan')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
    )
    text = models.TextField()
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    room_type = models.CharField(max_length=50, blank=True, help_text='e.g. Deluxe Room, Suite')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} ({self.rating}/5)"


class FAQ(models.Model):
    """Frequently asked questions — renders as FAQ schema for rich results."""
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('booking', 'Booking & Payment'),
        ('rooms', 'Rooms & Amenities'),
        ('location', 'Location & Transport'),
        ('policies', 'Policies'),
    ]

    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class NearbyAttraction(models.Model):
    """Nearby landmarks and attractions for location content."""
    CATEGORY_CHOICES = [
        ('landmark', 'Landmark'),
        ('shopping', 'Shopping'),
        ('hospital', 'Hospital'),
        ('restaurant', 'Restaurant'),
        ('transport', 'Transport'),
        ('government', 'Government'),
        ('education', 'Education'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    distance = models.CharField(max_length=50, help_text='e.g. 5 min drive, 2 km')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.distance})"

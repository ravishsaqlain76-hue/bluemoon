from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('ceo', 'CEO'),
        ('marketing', 'Marketing'),
        ('receptionist', 'Receptionist'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='guest')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    guest_house = models.ForeignKey(
        'core.Property', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='staff_profiles',
        help_text='Property this staff member is assigned to (null for CEO/guests)',
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_ceo(self):
        return self.role == 'ceo'

    @property
    def is_marketing(self):
        return self.role == 'marketing'

    @property
    def is_receptionist(self):
        return self.role == 'receptionist'

    @property
    def is_staff_role(self):
        return self.role in ('ceo', 'marketing', 'receptionist')


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled'),
        ('login', 'Logged In'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    guest_house = models.ForeignKey(
        'core.Property', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='activity_logs',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=50)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.target_model} at {self.timestamp:%Y-%m-%d %H:%M}"

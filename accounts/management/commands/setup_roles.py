from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create Django Groups with permissions matching the RBAC roles'

    def handle(self, *args, **options):
        self._create_ceo_group()
        self._create_receptionist_group()
        self._create_marketing_group()
        self.stdout.write(self.style.SUCCESS('All groups and permissions set up successfully.'))

    def _create_ceo_group(self):
        group, _ = Group.objects.get_or_create(name='CEO')
        all_perms = Permission.objects.all()
        group.permissions.set(all_perms)
        self.stdout.write(f'  CEO group: {all_perms.count()} permissions')

    def _create_receptionist_group(self):
        group, _ = Group.objects.get_or_create(name='Receptionist')
        group.permissions.clear()

        # Booking: view + change (approve/cancel)
        booking_ct = ContentType.objects.get(app_label='bookings', model='booking')
        booking_perms = Permission.objects.filter(
            content_type=booking_ct, codename__in=['view_booking', 'change_booking']
        )
        group.permissions.add(*booking_perms)

        # Room: view only
        room_ct = ContentType.objects.get(app_label='rooms', model='room')
        room_view = Permission.objects.filter(content_type=room_ct, codename='view_room')
        group.permissions.add(*room_view)

        # UserProfile: view only (to see guest info)
        profile_ct = ContentType.objects.get(app_label='accounts', model='userprofile')
        profile_view = Permission.objects.filter(content_type=profile_ct, codename='view_userprofile')
        group.permissions.add(*profile_view)

        self.stdout.write(f'  Receptionist group: {group.permissions.count()} permissions')

    def _create_marketing_group(self):
        group, _ = Group.objects.get_or_create(name='Marketing')
        group.permissions.clear()

        content_models = [
            ('core', 'seosettings'),
            ('core', 'pageseo'),
            ('core', 'testimonial'),
            ('core', 'faq'),
            ('core', 'nearbyattraction'),
        ]

        for app_label, model in content_models:
            ct = ContentType.objects.get(app_label=app_label, model=model)
            perms = Permission.objects.filter(content_type=ct)
            group.permissions.add(*perms)

        self.stdout.write(f'  Marketing group: {group.permissions.count()} permissions')

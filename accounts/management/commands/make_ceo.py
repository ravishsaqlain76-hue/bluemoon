from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Promote a user to CEO role (sets profile role, is_staff, and adds to CEO group)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to promote to CEO')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" not found.')

        # Set profile role
        profile = user.profile
        profile.role = 'ceo'
        profile.save()

        # Set is_staff so they can access /admin/
        user.is_staff = True
        user.save()

        # Add to CEO group
        ceo_group, _ = Group.objects.get_or_create(name='CEO')
        user.groups.add(ceo_group)

        self.stdout.write(self.style.SUCCESS(f'User "{username}" is now CEO.'))

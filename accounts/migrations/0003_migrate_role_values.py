from django.db import migrations


def migrate_roles_forward(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    UserProfile.objects.filter(role='staff').update(role='receptionist')
    UserProfile.objects.filter(role='admin').update(role='ceo')


def migrate_roles_backward(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    UserProfile.objects.filter(role='receptionist').update(role='staff')
    UserProfile.objects.filter(role='ceo').update(role='admin')
    UserProfile.objects.filter(role='marketing').update(role='staff')


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_alter_userprofile_role_activitylog'),
    ]

    operations = [
        migrations.RunPython(migrate_roles_forward, migrate_roles_backward),
    ]

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import UserProfile


ROLE_TO_GROUP = {
    'ceo': 'CEO',
    'marketing': 'Marketing',
    'receptionist': 'Receptionist',
}


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserProfile)
def sync_role_to_group(sender, instance, **kwargs):
    """When a profile role changes, sync the Django Group and is_staff flag."""
    user = instance.user
    group_name = ROLE_TO_GROUP.get(instance.role)

    # Remove from all role groups
    role_groups = Group.objects.filter(name__in=ROLE_TO_GROUP.values())
    for g in role_groups:
        user.groups.remove(g)

    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        if not user.is_staff:
            User.objects.filter(pk=user.pk).update(is_staff=True)
    else:
        # Guest role: remove staff access (but don't touch superusers)
        if user.is_staff and not user.is_superuser:
            User.objects.filter(pk=user.pk).update(is_staff=False)

from .models import ActivityLog


def log_activity(user, action, target_model, target_id=None, description='', guest_house=None):
    """
    Record an activity log entry.

    Usage:
        log_activity(request.user, 'update', 'Room', room.pk, 'Changed price from 5000 to 7000')
    """
    ActivityLog.objects.create(
        user=user,
        action=action,
        target_model=target_model,
        target_id=target_id,
        description=description,
        guest_house=guest_house,
    )

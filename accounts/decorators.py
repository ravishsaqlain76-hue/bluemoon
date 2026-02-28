from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):
    """
    Decorator that checks the user's UserProfile.role.
    Superusers bypass all role checks.

    Usage:
        @role_required('ceo')
        @role_required('ceo', 'receptionist')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            try:
                profile = request.user.profile
            except Exception:
                messages.error(request, 'Your account is not properly configured. Please contact an administrator.')
                return redirect('home')

            if profile.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

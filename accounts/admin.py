from django.contrib import admin
from .models import UserProfile, ActivityLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']
    list_editable = ['role']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'target_model', 'description']
    list_filter = ['action', 'target_model']
    search_fields = ['description', 'user__username']
    readonly_fields = ['user', 'action', 'target_model', 'target_id', 'description', 'timestamp']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

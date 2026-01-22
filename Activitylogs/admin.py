from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin interface for ActivityLog model"""
    list_display = ['id', 'user', 'activity_type', 'description_preview', 'ip_address', 'created_at']
    list_filter = ['activity_type', 'created_at', 'user']
    search_fields = ['user__username', 'user__email', 'description', 'ip_address']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'activity_type', 'description')
        }),
        ('Metadata', {
            'fields': ('metadata', 'ip_address', 'user_agent', 'created_at')
        }),
    )
    
    def description_preview(self, obj):
        """Show first 50 characters of description"""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description Preview'

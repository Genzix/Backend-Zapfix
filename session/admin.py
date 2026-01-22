from django.contrib import admin
from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin interface for Session model"""
    list_display = ['id', 'user', 'title', 'status', 'created_at', 'updated_at', 'last_activity_at', 'total_tokens_used', 'message_count']
    list_filter = ['status', 'created_at', 'user']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_activity_at']


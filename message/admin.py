from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model"""
    list_display = ['id', 'session', 'role', 'content_preview', 'tokens_used', 'model_used', 'created_at', 'sequence_number']
    list_filter = ['role', 'created_at', 'session__status']
    search_fields = ['content', 'session__title', 'session__user__username']
    readonly_fields = ['id', 'created_at', 'sequence_number']
    
    def content_preview(self, obj):
        """Return a short preview of the content for the admin list display."""
        if not obj or getattr(obj, "content", None) is None:
            return ""
        preview = str(obj.content)
        if len(preview) > 75:
            return preview[:72].rstrip() + "..."
        return preview
    content_preview.short_description = "Content preview"

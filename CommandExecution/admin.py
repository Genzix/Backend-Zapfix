from django.contrib import admin
from .models import CommandExecution


@admin.register(CommandExecution)
class CommandExecutionAdmin(admin.ModelAdmin):
    """Admin interface for CommandExecution model"""
    list_display = ['id', 'user', 'command_preview', 'command_type', 'status', 'execution_time_ms', 'created_at']
    list_filter = ['command_type', 'status', 'created_at', 'user']
    search_fields = ['command', 'user__username', 'user__email', 'hostname', 'ip_address']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'session', 'command', 'command_type', 'status')
        }),
        ('Execution Details', {
            'fields': ('output', 'exit_code', 'execution_time_ms', 'error_message')
        }),
        ('System Information', {
            'fields': ('hostname', 'ip_address', 'created_at')
        }),
    )
    
    def command_preview(self, obj):
        """Show first 50 characters of command"""
        return obj.command[:50] + '...' if len(obj.command) > 50 else obj.command
    command_preview.short_description = 'Command Preview'

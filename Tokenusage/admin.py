from django.contrib import admin
from .models import TokenUsage

@admin.register(TokenUsage)
class TokenUsageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session', 'message', 'model_used', 'tokens_input', 'tokens_output', 'tokens_total', 'cost_usd', 'created_at']
    list_filter = ['model_used', 'user', 'session']
    search_fields = ['user__username', 'model_used']
    readonly_fields = ['id', 'tokens_total', 'created_at']

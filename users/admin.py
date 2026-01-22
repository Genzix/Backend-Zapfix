from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    fk_name = 'user'  # Specify which ForeignKey to use
    can_delete = False
    verbose_name_plural = 'Profile'
    extra = 1  # Show one empty form for creating profile if missing


class UserAdmin(BaseUserAdmin):
    """Extended User admin with UserProfile - auto-creates profile if missing"""
    inlines = (UserProfileInline,)
    
    def save_model(self, request, obj, form, change):
        """Auto-create UserProfile if missing when saving user"""
        super().save_model(request, obj, form, change)
        # Auto-create profile if it doesn't exist
        if not hasattr(obj, 'profile'):
            # Create with default role 'user', but skip validation for auto-creation
            profile = UserProfile(user=obj, role='user')
            profile.save(validate=False)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile"""
    list_display = ['user', 'role', 'admin_id', 'created_at', 'updated_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Admin Relationship', {
            'fields': ('admin_id',),
            'description': "Required if role is 'user'. Must reference an admin user."
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )



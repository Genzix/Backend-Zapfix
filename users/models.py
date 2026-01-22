from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid


class UserProfile(models.Model):
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile',help_text="One-to-one relationship with Django User model")
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='user',help_text="User role: 'admin' or 'user'")
    admin_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_users',
        help_text="Required if role is 'user'. Must reference an admin user. NULL if role is 'admin'."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def clean(self):
        """Validate that users have an admin_id and admins don't"""
        if self.role == 'user' and not self.admin_id:
            raise ValidationError("Users must have an admin_id assigned.")
        if self.role == 'admin' and self.admin_id:
            raise ValidationError("Admins cannot have an admin_id.")
        if self.admin_id:
            try:
                if hasattr(self.admin_id, 'profile') and self.admin_id.profile.role != 'admin':
                    raise ValidationError("admin_id must reference a user with admin role.")
            except UserProfile.DoesNotExist:
                raise ValidationError("Admin user profile does not exist.")
    
    def save(self, *args, **kwargs):
        """Save with validation"""
        # Allow skipping validation with validate=False for special cases
        validate = kwargs.pop('validate', True)
        if validate:
            self.full_clean()
        super().save(*args, **kwargs)
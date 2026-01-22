from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile


class UserCreateSerializer(serializers.Serializer):
    """Serializer for creating User"""
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    admin_id = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)
    
    def validate_username(self, value):
        """Validate username uniqueness"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value
    
    def validate(self, attrs):
        """Validate role and admin_id relationship"""
        role = attrs.get('role')
        admin_id = attrs.get('admin_id')
        
        if role == 'user' and not admin_id:
            raise serializers.ValidationError({"admin_id": "Users must have an admin_id assigned."})
        if role == 'admin' and admin_id:
            raise serializers.ValidationError({"admin_id": "Admins cannot have an admin_id."})
        if admin_id:
            try:
                admin_user = User.objects.get(id=admin_id)
                if not hasattr(admin_user, 'profile') or admin_user.profile.role != 'admin':
                    raise serializers.ValidationError({"admin_id": "admin_id must reference a user with admin role."})
            except User.DoesNotExist:
                raise serializers.ValidationError({"admin_id": "Admin user with this ID does not exist."})
        
        return attrs
    
    def create(self, validated_data):
        """Create user and profile"""
        admin_id = validated_data.pop('admin_id', None)
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        
        # Create User
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=validated_data.get('is_active', True)
        )
        
        # Create UserProfile
        admin_user = User.objects.get(id=admin_id) if admin_id else None
        profile = UserProfile(user=user, role=role, admin_id=admin_user)
        profile.save(validate=False)  # Skip validation during creation to avoid circular dependency
        
        return user

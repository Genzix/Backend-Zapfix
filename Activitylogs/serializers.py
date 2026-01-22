from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user_id', 'username', 'activity_type', 'description',
            'metadata', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActivityLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating activity logs"""
    
    class Meta:
        model = ActivityLog
        fields = [
            'activity_type', 'description', 'metadata',
            'ip_address', 'user_agent'
        ]
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True},
            'metadata': {'required': False, 'allow_null': True},
            'ip_address': {'required': False, 'allow_null': True},
            'user_agent': {'required': False, 'allow_blank': True},
        }
    
    def create(self, validated_data):
        request = self.context['request']
        return ActivityLog.objects.create(
            user=request.user,
            **validated_data
        )


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics in admin dashboard"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_null=True)
    last_name = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(allow_null=True)
    last_login = serializers.DateTimeField(allow_null=True)
    total_sessions = serializers.IntegerField()
    total_tokens_used = serializers.IntegerField()
    total_commands_executed = serializers.IntegerField()


class UserActivitySerializer(serializers.Serializer):
    """Serializer for user activity in activity summary"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    sessions_count = serializers.IntegerField()
    commands_count = serializers.IntegerField()
    tokens_used = serializers.IntegerField()
    last_activity = serializers.DateTimeField(allow_null=True)


class ActivitySummarySerializer(serializers.Serializer):
    """Serializer for activity summary response"""
    summary = serializers.DictField()
    user_activity = UserActivitySerializer(many=True)


class TokensByModelSerializer(serializers.Serializer):
    """Serializer for tokens by model (dynamic dict)"""
    # This is a dynamic serializer for dict-like data
    pass


class RecentSessionSerializer(serializers.Serializer):
    """Serializer for recent sessions in user details"""
    id = serializers.UUIDField()
    title = serializers.CharField()
    created_at = serializers.DateTimeField()
    message_count = serializers.IntegerField()
    tokens_used = serializers.IntegerField()


class RecentCommandSerializer(serializers.Serializer):
    """Serializer for recent commands in user details"""
    id = serializers.UUIDField()
    command = serializers.CharField()
    command_type = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class UserStatisticsDetailSerializer(serializers.Serializer):
    """Serializer for user statistics in user details"""
    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    total_commands = serializers.IntegerField()
    total_tokens_used = serializers.IntegerField()
    tokens_by_model = serializers.DictField()


class UserInfoSerializer(serializers.Serializer):
    """Serializer for user info in user details"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    created_at = serializers.DateTimeField(allow_null=True)


class UserDetailsSerializer(serializers.Serializer):
    """Serializer for user details response"""
    user = UserInfoSerializer()
    statistics = UserStatisticsDetailSerializer()
    recent_sessions = RecentSessionSerializer(many=True)
    recent_commands = RecentCommandSerializer(many=True)


class UsersListResponseSerializer(serializers.Serializer):
    """Serializer for users list response"""
    users = UserStatisticsSerializer(many=True)


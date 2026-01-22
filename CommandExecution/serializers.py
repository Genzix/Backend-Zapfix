from rest_framework import serializers
from .models import CommandExecution

class CommandExecutionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating command execution"""
    session_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = CommandExecution
        fields = [
            'session_id', 'command', 'command_type', 'output',
            'exit_code', 'execution_time_ms', 'status',
            'error_message', 'hostname', 'ip_address'
        ]
        extra_kwargs = {
            'output': {'required': False, 'allow_blank': True},
            'exit_code': {'required': False, 'allow_null': True},
            'execution_time_ms': {'required': False, 'allow_null': True},
            'error_message': {'required': False, 'allow_blank': True},
            'hostname': {'required': False, 'allow_blank': True},
            'ip_address': {'required': False, 'allow_null': True},
        }
    
    def create(self, validated_data):
        request = self.context['request']
        session_id = validated_data.pop('session_id', None)
        
        # Get session if session_id provided
        session = None
        if session_id:
            from session.models import Session
            try:
                session = Session.objects.get(pk=session_id, user=request.user)
            except Session.DoesNotExist:
                pass  # session_id is optional, so we continue without it
        
        return CommandExecution.objects.create(
            user=request.user,
            session=session,
            **validated_data
        )


class CommandExecutionListSerializer(serializers.ModelSerializer):
    """Serializer for listing command executions"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    session_id = serializers.UUIDField(source='session.id', read_only=True, allow_null=True)
    
    class Meta:
        model = CommandExecution
        fields = [
            'id', 'user_id', 'username', 'session_id', 'command',
            'command_type', 'status', 'execution_time_ms', 'created_at'
        ]
        read_only_fields = ['id', 'user_id', 'username', 'session_id', 'created_at']


class CommandExecutionDetailSerializer(serializers.ModelSerializer):
    """Serializer for command execution detail"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    session_id = serializers.UUIDField(source='session.id', read_only=True, allow_null=True)
    
    class Meta:
        model = CommandExecution
        fields = [
            'id', 'user_id', 'username', 'session_id', 'command',
            'command_type', 'output', 'exit_code', 'execution_time_ms',
            'status', 'error_message', 'hostname', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'user_id', 'username', 'session_id', 'created_at']


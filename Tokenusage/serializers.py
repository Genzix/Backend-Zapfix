from rest_framework import serializers
from .models import TokenUsage


class TokenUsageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating token usage records"""
    session_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    message_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = TokenUsage
        fields = [
            'session_id', 'message_id', 'model_used', 
            'tokens_input', 'tokens_output', 'tokens_total', 'cost_usd'
        ]
        extra_kwargs = {
            'cost_usd': {'required': False, 'allow_null': True},
        }
    
    def create(self, validated_data):
        request = self.context['request']
        session_id = validated_data.pop('session_id', None)
        message_id = validated_data.pop('message_id', None)
        
        # Get session if session_id provided
        session = None
        if session_id:
            from session.models import Session
            try:
                session = Session.objects.get(pk=session_id, user=request.user)
            except Session.DoesNotExist:
                pass  # session_id is optional
        
        # Get message if message_id provided
        message = None
        if message_id:
            from message.models import Message
            try:
                message = Message.objects.get(pk=message_id, session__user=request.user)
            except Message.DoesNotExist:
                pass  # message_id is optional
        
        return TokenUsage.objects.create(
            user=request.user,
            session=session,
            message=message,
            **validated_data
        )


class TokenUsageResponseSerializer(serializers.ModelSerializer):
    """Serializer for token usage creation response"""
    
    class Meta:
        model = TokenUsage
        fields = ['id', 'tokens_total', 'created_at']
        read_only_fields = ['id', 'tokens_total', 'created_at']

from rest_framework import serializers
from .models import Session
from message.models import Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    class Meta:
        model = Message
        ref_name = 'SessionMessageSerializer'
        fields = [
            'id', 'role', 'content', 'tokens_used', 
            'model_used', 'created_at', 'sequence_number'
        ]
        read_only_fields = ['id', 'created_at', 'sequence_number']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ['role', 'content', 'tokens_used', 'model_used']


class SessionListSerializer(serializers.ModelSerializer):
    """Serializer for listing sessions (without messages)"""
    
    class Meta:
        model = Session
        fields = [
            'id', 'title', 'status', 'created_at', 'updated_at',
            'last_activity_at', 'total_tokens_used', 'message_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_activity_at',
            'total_tokens_used', 'message_count'
        ]


class SessionDetailSerializer(serializers.ModelSerializer):
    """Serializer for session detail with messages"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Session
        fields = [
            'id', 'title', 'status', 'created_at', 'updated_at',
            'last_activity_at', 'total_tokens_used', 'message_count', 'messages'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_activity_at',
            'total_tokens_used', 'message_count', 'messages'
        ]


class SessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating session"""
    
    class Meta:
        model = Session
        fields = ['title']

    def create(self, validated_data):
        request = self.context['request']
        return Session.objects.create(
            user=request.user,
            title=validated_data.get('title', '')
        )
    

class SessionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating session"""
    
    class Meta:
        model = Session
        fields = ['title', 'status']

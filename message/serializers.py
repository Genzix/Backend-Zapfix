from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    session_id = serializers.UUIDField(source='session.id', read_only=True)
    #session_title = serializers.CharField(source='session.title', read_only=True)
    
    class Meta:
        model = Message
        ref_name = 'MessageSerializer'
        fields = [
            'id', 'session_id',  'role', 'content',
            'tokens_used', 'model_used', 'created_at', 'sequence_number'
        ]
        read_only_fields = ['id', 'session_id',  'created_at', 'sequence_number']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ['role', 'content', 'tokens_used', 'model_used']
        extra_kwargs = {
            'tokens_used': {'required': False, 'default': 0},
            'model_used': {'required': False, 'allow_null': True, 'allow_blank': True},
        }


class MessageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating messages"""
    
    class Meta:
        model = Message
        fields = ['content', 'tokens_used', 'model_used']
        extra_kwargs = {
            'content': {'required': False},
            'tokens_used': {'required': False},
            'model_used': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

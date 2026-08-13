from rest_framework import serializers
from .models import NewsUsers, Conversation, Message

class ConversationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Conversation
        fields = ['id', 'user']

class MessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'text', 'is_from_user']
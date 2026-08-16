from rest_framework import serializers
from .models import (
    NewsUsers,
    Conversation,
    Message,
    Law,
    Article,
)


class ConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "text",
            "is_from_user",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class LawSerializer(serializers.ModelSerializer):

    class Meta:
        model = Law
        fields = [
            "id",
            "title",
            "content",
            "source_url",
        ]
        read_only_fields = ["id"]


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = [
            "id",
            "law",
            "number",
            "title",
            "content",
        ]
        read_only_fields = ["id"]
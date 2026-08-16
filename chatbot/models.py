from django.db import models
from django.contrib.auth.models import AbstractUser
from pgvector.django import VectorField


class NewsUsers(AbstractUser):
    pass


class Conversation(models.Model):
    user = models.ForeignKey(
        NewsUsers,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Conversation"
        ordering = ["-updated_at"]

    def __str__(self):
        if self.user:
            return f"{self.user.username} - Conversation {self.id}"
        return f"Anonymous - Conversation {self.id}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    text = models.TextField()
    is_from_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Message"
        ordering = ["created_at"]

    def __str__(self):
        sender = "User" if self.is_from_user else "Bot"
        return f"{sender} - Conversation {self.conversation_id}"


class Law(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    source_url = models.URLField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = "Law"
        ordering = ["title"]

    def __str__(self):
        return self.title

class Article(models.Model):
    law = models.ForeignKey(
        Law,
        on_delete=models.CASCADE,
        related_name="articles"
    )

    number = models.CharField(max_length=50)

    title = models.CharField(
        max_length=500,
        blank=True
    )

    content = models.TextField()

    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "Article"
        ordering = ["law", "number"]

    def __str__(self):
        return f"{self.law.title} - Maddə {self.number}"
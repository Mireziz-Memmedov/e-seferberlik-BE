from django.db import models
from django.contrib.auth.models import AbstractUser

class NewsUsers(AbstractUser):
    pass

class Conversation(models.Model):
    user = models.ForeignKey(
        NewsUsers,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='conversations'
    )

    class Meta:
        db_table = 'Conversation'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')

    text = models.TextField()
    is_from_user = models.BooleanField(default=True)

    class Meta:
        db_table = 'Message'
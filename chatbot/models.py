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


class Law(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    source_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'Law'

    def __str__(self):
        return self.title

class Article(models.Model):
    law = models.ForeignKey(
        Law,
        on_delete=models.CASCADE,
        related_name='articles'
    )

    number = models.CharField(max_length=50)
    title = models.CharField(max_length=500, blank=True)
    content = models.TextField()

    class Meta:
        db_table = 'Article'

    def __str__(self):
        return f"{self.law.title} - Maddə {self.number}"
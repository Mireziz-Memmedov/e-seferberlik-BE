from django.contrib import admin
from .models import Law, Article, Conversation, Message, NewsUsers


@admin.register(Law)
class LawAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "source_url")
    search_fields = ("title", "content")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "law", "number", "title")
    search_fields = ("number", "title", "content", "law__title")
    list_filter = ("law",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("user__username",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "is_from_user", "created_at")
    search_fields = ("text",)
    list_filter = ("is_from_user",)


@admin.register(NewsUsers)
class NewsUsersAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")
from django.contrib import admin
from .models import ChatSession, Message

# Inline messages inside a chat session
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'text', 'created_at')
    can_delete = True

# ChatSession admin
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    inlines = [MessageInline]
    search_fields = ('title',)

# Optional: separate admin for messages
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'created_at', 'text_preview')
    list_filter = ('session', 'sender', 'created_at')
    search_fields = ('text', 'sender')

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Message'

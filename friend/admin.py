from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_participants')
    search_fields = ('name',)
    filter_horizontal = ('participants',)

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chatroom', 'sender', 'content_preview', 'timestamp')
    search_fields = ('sender__username', 'content')
    list_filter = ('timestamp',)
    readonly_fields = ('timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] if obj.content else 'Image Only'
    content_preview.short_description = 'Content Preview'

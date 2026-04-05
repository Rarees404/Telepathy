from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Chat, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Encryption Keys', {
            'fields': ('public_key', 'signing_public_key'),
        }),
        ('Two-Factor Auth', {
            'fields': ('totp_secret', 'is_2fa_enabled'),
        }),
    )
    list_display = ('username', 'email', 'is_2fa_enabled', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('pin', 'user1', 'user2', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('pin', 'user1__username', 'user2__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username')
    readonly_fields = ('id', 'timestamp')

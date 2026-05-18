from django.contrib import admin
from .models import Message, Habit

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'text', 'timestamp', 'owner']
    list_filter = ['sender']

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'category', 'streak', 'longest_streak', 'is_active', 'last_checked']
    list_filter = ['category', 'is_active']

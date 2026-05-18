from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    SENDER_CHOICES = [('user', 'User'), ('bot', 'Bot')]
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.sender}] {self.text[:50]}"


class Habit(models.Model):
    CATEGORY_CHOICES = [
        ('fitness', 'Fitness'), ('book', 'Reading'), ('water', 'Hydration'),
        ('sleep', 'Sleep'), ('food', 'Nutrition'), ('mind', 'Mindfulness'),
        ('code', 'Coding'), ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_checked = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Habit'

    def __str__(self):
        return self.name

    def check_in_today(self):
        today = timezone.localdate()
        if self.last_checked == today:
            return False, "already"
        yesterday = today - timezone.timedelta(days=1)
        if self.last_checked == yesterday:
            self.streak += 1
        else:
            self.streak = 1
        if self.streak > self.longest_streak:
            self.longest_streak = self.streak
        self.last_checked = today
        self.save()
        return True, self.streak

    def is_done_today(self):
        return self.last_checked == timezone.localdate()

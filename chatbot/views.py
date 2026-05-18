import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Message, Habit
from .bot_logic import get_bot_response


# ── Auth Views ──────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if not username or not password:
            error = 'Please fill in all fields.'
        elif password != password2:
            error = 'Passwords do not match.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already taken. Choose another.'
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('chat')
    return render(request, 'chatbot/register.html', {'error': error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('chat')
        else:
            error = 'Invalid username or password.'
    return render(request, 'chatbot/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Main Chat View ───────────────────────────────────────────────

@login_required(login_url='login')
def chat_view(request):
    user = request.user
    messages = Message.objects.filter(owner=user)

    if not messages.exists():
        welcome = (
            f"Welcome back, **{user.username}**!\n\n"
            "I'm HabitBot -- your personal habit coach.\n"
            "Your habits and history are saved to your account.\n\n"
            "Type **help** to see all commands, or start right away:\n"
            "**add habit drink 2L of water**"
        )
        Message.objects.create(sender='bot', text=welcome, owner=user)
        messages = Message.objects.filter(owner=user)

    habits = Habit.objects.filter(owner=user, is_active=True).order_by('created_at')
    today = timezone.localdate()

    return render(request, 'chatbot/chat.html', {
        'messages': messages,
        'habits': habits,
        'today': today,
    })


@login_required(login_url='login')
@require_POST
def send_message(request):
    user = request.user
    try:
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not user_text:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    if len(user_text) > 500:
        return JsonResponse({'error': 'Message too long'}, status=400)

    Message.objects.create(sender='user', text=user_text, owner=user)
    bot_response = get_bot_response(user_text, user)
    Message.objects.create(sender='bot', text=bot_response, owner=user)

    habits = Habit.objects.filter(owner=user, is_active=True).order_by('created_at')
    today = timezone.localdate()
    habits_data = [
        {'name': h.name, 'streak': h.streak, 'done_today': h.last_checked == today, 'category': h.category}
        for h in habits
    ]

    return JsonResponse({'user_message': user_text, 'bot_response': bot_response, 'habits': habits_data})


@login_required(login_url='login')
@require_POST
def clear_history(request):
    Message.objects.filter(owner=request.user).delete()
    return JsonResponse({'status': 'ok'})

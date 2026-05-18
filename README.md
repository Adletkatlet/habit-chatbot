# Daily Habit Tracker — HabitBot

A Django-powered chatbot for building and tracking daily habits.

## Technologies
- Python 3.10+ / Django 5.0
- SQLite database
- HTML / CSS / JavaScript (AJAX)
- Django Sessions

## Project Structure
```
habit_chatbot/
├── manage.py
├── requirements.txt
├── habit_chatbot/       # Main config
│   ├── settings.py
│   └── urls.py
└── chatbot/             # App
    ├── models.py        # Message + Habit models
    ├── views.py         # Request handlers
    ├── urls.py          # Routes
    ├── bot_logic.py     # Bot brain
    └── templates/chatbot/chat.html
```

## Installation & Run

```bash
pip install -r requirements.txt
python manage.py makemigrations chatbot
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## Commands
| Command | Description |
|---------|-------------|
| `add habit [name]` | Add a new habit |
| `my habits` | View habits + today's status |
| `done [name]` | Check off a habit for today |
| `streak [name]` | View streak for a habit |
| `progress` | Weekly progress report |
| `stats` | Overall statistics |
| `tips` | Habit-building advice |
| `quote` | Inspirational quote |
| `science` | The science of habits |
| `help` | Show all commands |

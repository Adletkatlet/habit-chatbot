import random
from django.utils import timezone
from .models import Habit


RESPONSES = {
    'greeting': {
        'keywords': ['hello', 'hi', 'hey', 'good morning', 'good evening', 'sup', 'yo', 'hiya'],
        'answers': [
            "Hey there, champion! Ready to crush your habits today? Type **help** to see what I can do!",
            "Hello! I'm HabitBot, your personal habit coach. Type **help** to get started!",
            "Hey! Great to see you. Let's build some awesome habits together! Type **help** for commands.",
        ]
    },
    'help': {
        'keywords': ['help', 'commands', 'what can you do', 'menu', 'options', 'guide'],
        'answers': [
            """Here's everything I can do for you:

TRACKING YOUR HABITS:
  add habit [name] -- add a new habit to track
  my habits -- view all your habits + today's progress
  done [habit name] -- check off a habit for today
  streak [habit name] -- see your streak for a habit
  delete habit [name] -- remove a habit
  progress -- see your full weekly progress

MOTIVATION & TIPS:
  tips -- get habit-building tips
  quote -- get an inspirational quote
  science -- learn the science behind habits
  morning routine -- ideas for morning habits
  evening routine -- ideas for evening habits

OTHER:
  stats -- your overall statistics
  reset -- clear all habits
  hello -- say hi!"""
        ]
    },
    'tips': {
        'keywords': ['tips', 'advice', 'how to build', 'suggestion', 'trick'],
        'answers': [
            """Top 5 Habit-Building Tips:

1. Start Tiny
   Don't aim for 30 min of exercise -- start with just 5 minutes. Small wins build momentum!

2. Stack Your Habits
   Attach new habits to existing ones:
   "After I brush my teeth, I will meditate for 2 minutes."

3. Never Miss Twice
   Missed a day? That's okay. But never miss two days in a row -- that's where habits die.

4. Make It Obvious
   Put your book on your pillow. Set your workout clothes out the night before.

5. Track Your Streak
   Use me to track your streak! Nothing motivates like not breaking the chain.

Type **add habit [name]** to start tracking today!""",
            """The 5 Laws of Behavior Change:

Make it OBVIOUS -- design your environment
Make it ATTRACTIVE -- pair with something enjoyable
Make it EASY -- reduce friction, start small
Make it SATISFYING -- reward yourself
Make it CONSISTENT -- same time, same place

From James Clear's "Atomic Habits" -- a must-read!"""
        ]
    },
    'quote': {
        'keywords': ['quote', 'inspire', 'motivation', 'motivate', 'inspire me'],
        'answers': [
            "\"We are what we repeatedly do. Excellence, then, is not an act, but a habit.\" -- Aristotle",
            "\"You do not rise to the level of your goals. You fall to the level of your systems.\" -- James Clear",
            "\"The secret of your future is hidden in your daily routine.\" -- Mike Murdock",
            "\"Motivation gets you going, but habit gets you there.\" -- Zig Ziglar",
            "\"Small daily improvements are the key to staggering long-term results.\" -- Robin Sharma",
            "\"First forget inspiration. Habit is more dependable.\" -- Octavia Butler",
        ]
    },
    'science': {
        'keywords': ['science', 'research', 'how long', '21 days', '66 days', 'brain', 'psychology'],
        'answers': [
            """The Science of Habits:

The Habit Loop (Charles Duhigg):
  CUE --> ROUTINE --> REWARD

Your brain creates a neurological loop that becomes automatic over time.

How long does it actually take?
A 2010 study by Phillippa Lally at UCL found:
  Average: 66 days (not the myth of 21!)
  Range: 18 to 254 days

The Compound Effect:
  1% better every day = 37x better in a year

Key insight: You don't need willpower -- you need SYSTEMS."""
        ]
    },
    'morning': {
        'keywords': ['morning routine', 'morning habits', 'wake up', 'start the day'],
        'answers': [
            """Ideal Morning Routine Habits:

  No phone for the first 30 minutes
  Drink a glass of water right away
  5-10 min light stretching or exercise
  Journal for 5 minutes (3 things you're grateful for)
  Plan your top 3 tasks for the day
  Eat a protein-rich breakfast

Pro tip: Pick ONE and nail it for 2 weeks before adding another.
Type: **add habit morning walk**"""
        ]
    },
    'evening': {
        'keywords': ['evening routine', 'night habits', 'before bed', 'bedtime', 'sleep routine'],
        'answers': [
            """Evening Routine for Better Sleep:

  No screens 1 hour before bed
  Write tomorrow's top 3 priorities
  Read for 20 minutes
  Consistent sleep time (same every night!)
  Write 3 wins from today

The evening routine sets up your success for the next day!"""
        ]
    },
    'goodbye': {
        'keywords': ['bye', 'goodbye', 'see you', 'later', 'exit', 'quit', 'thanks'],
        'answers': [
            "Keep going -- consistency is everything! See you tomorrow!",
            "Great work! Remember: every habit check-in is a vote for the person you want to become. Bye!",
            "You've got this! See you next time. Don't forget to check in tomorrow!",
        ]
    },
}

CATEGORY_KEYWORDS = {
    'fitness': ['workout', 'exercise', 'run', 'gym', 'walk', 'yoga', 'pushup', 'squat', 'sport', 'training', 'steps'],
    'book': ['read', 'book', 'pages', 'study', 'learn', 'article'],
    'water': ['water', 'hydrat', 'drink'],
    'sleep': ['sleep', 'bed', 'wake', 'rest'],
    'food': ['eat', 'diet', 'food', 'meal', 'nutrition', 'vegetable', 'fruit', 'cook'],
    'mind': ['meditat', 'journal', 'breath', 'mindful', 'grateful', 'gratitude'],
    'code': ['code', 'program', 'leetcode', 'project', 'develop'],
}

STREAK_MESSAGES = {
    1: "You've started your journey! Day 1 complete!",
    3: "3 days in a row! You're building momentum!",
    7: "ONE WEEK STREAK! You're on fire!",
    14: "Two weeks strong! This is becoming a real habit!",
    21: "21 days! Keep going!",
    30: "30 DAY STREAK! You're absolutely incredible!",
    50: "50 DAYS! You're in the top 1% of habit-keepers!",
    66: "66 DAYS! Science says your habit is now automatic. LEGEND!",
    100: "100 DAYS! You are unstoppable. Hall of Fame status!",
}


def detect_category(name):
    name_lower = name.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return cat
    return 'other'


def get_bot_response(user_text, user):
    if not user_text or not user_text.strip():
        return "Please type something! Try **help** to see available commands."

    text = user_text.strip()
    text_lower = text.lower()

    if len(text) > 500:
        return "Message too long! Please keep it under 500 characters."

    if text_lower.startswith('add habit'):
        name = text[9:].strip()
        if not name:
            return "Please tell me the habit name!\nExample: **add habit drink 2L of water**"
        return _add_habit(name, user)

    if text_lower.startswith('done ') or text_lower.startswith('check '):
        prefix = 'done ' if text_lower.startswith('done ') else 'check '
        name = text[len(prefix):].strip()
        if not name:
            return "Which habit did you complete? Example: **done morning run**"
        return _check_habit(name, user)

    if text_lower.startswith('delete habit'):
        name = text[12:].strip()
        if not name:
            return "Which habit to delete? Example: **delete habit morning run**"
        return _delete_habit(name, user)

    if text_lower.startswith('streak '):
        name = text[7:].strip()
        return _get_streak(name, user)

    if any(p in text_lower for p in ['my habits', 'list habits', 'show habits', 'all habits']):
        return _get_habits(user)

    if any(p in text_lower for p in ['progress', 'weekly', 'how am i doing', 'overview']):
        return _get_progress(user)

    if any(p in text_lower for p in ['stats', 'statistics', 'my stats', 'overall']):
        return _get_stats(user)

    if text_lower in ['reset', 'clear all', 'delete all', 'start over']:
        return _reset_habits(user)

    for category, data in RESPONSES.items():
        if not data['answers']:
            continue
        for keyword in data['keywords']:
            if keyword in text_lower:
                return random.choice(data['answers'])

    return _unknown(text)


def _add_habit(name, user):
    if Habit.objects.filter(name__iexact=name, owner=user, is_active=True).exists():
        return f"You're already tracking **{name}**!\nType **my habits** to see your full list."
    category = detect_category(name)
    Habit.objects.create(name=name, category=category, owner=user)
    cat_labels = {
        'fitness': 'Fitness', 'book': 'Reading', 'water': 'Hydration',
        'sleep': 'Sleep', 'food': 'Nutrition', 'mind': 'Mindfulness',
        'code': 'Coding', 'other': 'General'
    }
    cat_label = cat_labels.get(category, 'General')
    return (
        f"Habit added: **{name}**\n"
        f"Category: {cat_label}\n\n"
        f"When you complete it today, type:\n"
        f"**done {name}**\n\n"
        f"Consistency is everything -- good luck!"
    )


def _check_habit(name, user):
    habit = Habit.objects.filter(name__icontains=name, owner=user, is_active=True).first()
    if not habit:
        return f"I couldn't find a habit matching **{name}**.\nType **my habits** to see your list."
    success, result = habit.check_in_today()
    if not success:
        return (
            f"You already checked in **{habit.name}** today!\n"
            f"Current streak: {habit.streak} days\n\n"
            f"Come back tomorrow to keep the streak going!"
        )
    streak = result
    streak_msg = STREAK_MESSAGES.get(streak, f"Day {streak} -- keep the chain alive!")
    congrats = random.choice(["Boom!", "Nailed it!", "That's what I'm talking about!", "Legend!", "You rock!"])
    return (
        f"{congrats} **{habit.name}** checked off for today!\n\n"
        f"Current streak: {streak} day{'s' if streak != 1 else ''}\n"
        f"Best streak: {habit.longest_streak} days\n\n"
        f"{streak_msg}"
    )


def _get_habits(user):
    habits = Habit.objects.filter(owner=user, is_active=True).order_by('created_at')
    if not habits:
        return (
            "You have no habits yet!\n\n"
            "Start with something small:\n"
            "  **add habit drink 2L of water**\n"
            "  **add habit read 10 pages**\n"
            "  **add habit morning walk**"
        )
    today = timezone.localdate()
    done_count = sum(1 for h in habits if h.last_checked == today)
    total = habits.count()
    lines = [f"Your Habits -- {done_count}/{total} done today\n"]
    for habit in habits:
        done = habit.last_checked == today
        streak_info = f"Streak: {habit.streak}d" if habit.streak > 0 else "No streak yet"
        lines.append(f"  {'[x]' if done else '[ ]'} {habit.name}  |  {streak_info}  |  {'DONE' if done else 'pending'}")
    if done_count == total and total > 0:
        lines.append("\nPERFECT DAY! All habits complete!")
    elif done_count == 0:
        lines.append("\nLet's go! Type **done [habit name]** when you complete one.")
    else:
        lines.append(f"\n{total - done_count} habit(s) left. You can do it!")
    return "\n".join(lines)


def _get_streak(name, user):
    habit = Habit.objects.filter(name__icontains=name, owner=user, is_active=True).first()
    if not habit:
        return f"No habit found matching **{name}**.\nType **my habits** to see your list."
    done_today = habit.last_checked == timezone.localdate()
    return (
        f"Streak for: **{habit.name}**\n\n"
        f"Current streak: {habit.streak} day{'s' if habit.streak != 1 else ''}\n"
        f"Best streak: {habit.longest_streak} day{'s' if habit.longest_streak != 1 else ''}\n"
        f"Today: {'Done!' if done_today else 'Not yet'}\n\n"
        f"{'Keep it going!' if habit.streak > 0 else 'Start your streak today!'}"
    )


def _get_progress(user):
    habits = Habit.objects.filter(owner=user, is_active=True)
    if not habits:
        return "No habits to show progress for. Add some with **add habit [name]**!"
    today = timezone.localdate()
    lines = ["Weekly Progress Report\n"]
    for habit in habits:
        done = habit.last_checked == today
        bar_filled = min(habit.streak, 7)
        bar = "[" + "#" * bar_filled + "-" * (7 - bar_filled) + "]"
        lines.append(f"  {habit.name}")
        lines.append(f"  {bar}  Streak: {habit.streak}d  Today: {'Done' if done else 'Pending'}\n")
    total = habits.count()
    done_today = sum(1 for h in habits if h.last_checked == today)
    lines.append(f"Today's completion: {done_today}/{total} ({int(done_today/total*100) if total else 0}%)")
    return "\n".join(lines)


def _get_stats(user):
    habits = Habit.objects.filter(owner=user, is_active=True)
    if not habits:
        return "No habits tracked yet. Start with **add habit [name]**!"
    today = timezone.localdate()
    total = habits.count()
    done_today = sum(1 for h in habits if h.last_checked == today)
    best_streak = max((h.longest_streak for h in habits), default=0)
    top_habit = max(habits, key=lambda h: h.longest_streak, default=None)
    return (
        f"Your Stats\n\n"
        f"Total habits tracked: {total}\n"
        f"Completed today: {done_today}/{total}\n"
        f"Best streak ever: {best_streak} days\n"
        f"Top habit: {top_habit.name if top_habit else 'N/A'}\n\n"
        f"{'Amazing consistency!' if best_streak >= 7 else 'Keep building those streaks!'}"
    )


def _delete_habit(name, user):
    habit = Habit.objects.filter(name__icontains=name, owner=user, is_active=True).first()
    if not habit:
        return f"No habit found matching **{name}**."
    habit_name = habit.name
    habit.is_active = False
    habit.save()
    return f"Habit **{habit_name}** removed from your tracker."


def _reset_habits(user):
    count = Habit.objects.filter(owner=user, is_active=True).update(is_active=False)
    if count == 0:
        return "No active habits to clear."
    return f"All {count} habits cleared. Fresh start!"


def _unknown(text):
    responses = [
        f"I'm not sure what you mean by \"{text[:40]}\".\nType **help** to see all commands!",
        "Hmm, I didn't get that. Try typing **help** for a list of commands!",
        "I couldn't understand that one. Type **help** to see what I can do!",
    ]
    return random.choice(responses)

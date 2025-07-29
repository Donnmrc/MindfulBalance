def get_mental_tip(self, mood_level: int) -> str:
    """Return a mental health tip based on mood level."""
    if mood_level <= 2:
        return "It's okay to feel down. Try talking to a friend or practicing deep breathing."
    elif mood_level <= 4:
        return "Take a short walk or listen to your favorite music to lift your mood."
    elif mood_level <= 6:
        return "Keep going! A little self-care goes a long way."
    elif mood_level <= 8:
        return "Great job! Remember to share your positivity with others."
    else:
        return "You're doing amazing! Keep up the positive mindset!"




def get_mental_tip(self, mood_level: int) -> str:
    """Return a mental health tip based on mood level."""
    if mood_level == 1:
        return "It's okay to feel very bad. Reach out to someone you trust and take care of yourself."
    elif mood_level == 3:
        return "Not feeling great? Try some deep breathing or a short walk to lift your spirits."
    elif mood_level == 5:
        return "Feeling okay is a good start. Consider writing down something you're grateful for."
    elif mood_level == 7:
        return "Good mood! Keep up the positive habits and share your smile with others."
    elif mood_level == 10:
        return "That's a great mood! Keep being happy and spread your joy!"
    else:
        return "Take care of yourself and remember every mood is valid."

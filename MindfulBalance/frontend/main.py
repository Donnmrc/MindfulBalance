import flet as ft
import httpx
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"
DEFAULT_USER = "test123"

# Color scheme
PRIMARY_COLOR = ft.Colors.BLUE_600
SECONDARY_COLOR = ft.Colors.BLUE_100
BACKGROUND_COLOR = ft.Colors.GREY_50
TEXT_COLOR = ft.Colors.GREY_900
CARD_COLOR = ft.Colors.WHITE

def home_view(page: ft.Page):
    # Fetch stats from API
    mood_stats = {}
    journal_count = 0
    streak = 0
    latest_journal = ""
    
    try:
        # Get mood stats
        response = httpx.get(f"{API_BASE}/stats", params={"username": DEFAULT_USER}, timeout=5)
        if response.status_code == 200:
            mood_stats = response.json().get("mood_stats", {})
        
        # Get journal count (would need to add this endpoint to your API)
        journal_response = httpx.get(f"{API_BASE}/journal_count", params={"username": DEFAULT_USER}, timeout=5)
        if journal_response.status_code == 200:
            journal_count = journal_response.json().get("count", 0)
            
        # Get streak (would need to implement this in your API)
        streak_response = httpx.get(f"{API_BASE}/streak", params={"username": DEFAULT_USER}, timeout=5)
        if streak_response.status_code == 200:
            streak = streak_response.json().get("streak", 0)
        
        # Get latest journal entry
        journal_entry_response = httpx.get(f"{API_BASE}/latest_journal", params={"username": DEFAULT_USER}, timeout=5)
        if journal_entry_response.status_code == 200:
            journal_data = journal_entry_response.json()
            latest_journal = journal_data.get("content", "")
            timestamp = journal_data.get("timestamp")
            if timestamp:
                # Convert ISO timestamp to more readable format
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
            else:
                formatted_time = None
    except:
        pass

    # Today's Mood Card
    today_mood = "Not tracked yet"
    if mood_stats:
        # Check if mood was logged today (simplified check)
        today_mood = f"{sum(mood_stats.values())} tracked"

    mood_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Today's Mood", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(today_mood, size=24, weight=ft.FontWeight.BOLD),
                ft.FilledButton(
                    "Track your first mood",
                    on_click=lambda _: page.go("/mood"),
                    height=40
                )
            ], spacing=10),
            padding=20,
            width=180,
            height=180
        ),
        color=CARD_COLOR,
        elevation=2,
        margin=5
    )

    # Streak Card
    streak_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Mood Streak", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"{streak} days", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Start your journey today", size=12)
            ], spacing=10),
            padding=20,
            width=180,
            height=180
        ),
        color=CARD_COLOR,
        elevation=2,
        margin=5
    )

    # Journal Card
    journal_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Journal Entries", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(str(journal_count), size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Total reflections written", size=12)
            ], spacing=10),
            padding=20,
            width=180,
            height=180
        ),
        color=CARD_COLOR,
        elevation=2,
        margin=5
    )

    # Quick Mood Check Section
    mood_check = ft.Container(
        content=ft.Column([
            ft.Text("Quick Mood Check", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("How are you feeling right now? Track your mood in seconds.", size=14),
            ft.FilledButton(
                "Track My Mood",
                on_click=lambda _: page.go("/mood"),
                width=200,
                height=50
            )
        ], spacing=10),
        padding=20,
        bgcolor=SECONDARY_COLOR,
        border_radius=10,
        margin=0,  # Remove margin for side-by-side alignment
        expand=1
    )

    # Daily Reflection Section
    daily_reflection = ft.Container(
        content=ft.Column([
            ft.Text("Daily Reflection", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Take a moment to reflect on your day and thoughts.", size=14),
            ft.FilledButton(
                "Write in Journal",
                on_click=lambda _: page.go("/journal"),
                width=200,
                height=50
            )
        ], spacing=10),
        padding=20,
        bgcolor=SECONDARY_COLOR,
        border_radius=10,
        margin=0,  # Remove margin for side-by-side alignment
        expand=1
    )

    # Update Latest Journal Section
    latest_journal_card = ft.Container(
        content=ft.Column([
            ft.Text("Latest Journal Entry", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(
                latest_journal if latest_journal else "No journal entry yet.", 
                size=14, 
                italic=True, 
                color=ft.Colors.GREY_700,
                text_align=ft.TextAlign.JUSTIFY
            ),
            ft.Text(
                formatted_time if formatted_time else "", 
                size=12,
                color=ft.Colors.GREY_600,
                italic=True
            ) if latest_journal else ft.Container(),
        ], spacing=10),
        padding=20,
        bgcolor=SECONDARY_COLOR,
        border_radius=10,
        margin=10
    )

    return ft.View(
        "/",
        controls=[
            ft.Text("Welcome back!", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("How are you feeling today? Let's check in with yourself.", size=16),
            ft.Row(
                [mood_card, streak_card, journal_card],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                wrap=True
            ),
            latest_journal_card,
            ft.Row(
                [mood_check, daily_reflection],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
        ],
        padding=20,
        spacing=20,
        bgcolor=BACKGROUND_COLOR
    )

def mood_view(page: ft.Page):
    mood_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("😊 Happy"),
            ft.dropdown.Option("😢 Sad"),
            ft.dropdown.Option("😫 Stressed"),
            ft.dropdown.Option("😌 Calm"),
            ft.dropdown.Option("😐 Neutral"),
            ft.dropdown.Option("😡 Angry"),
            ft.dropdown.Option("😃 Excited"),
            ft.dropdown.Option("😴 Tired"),
        ],
        label="How are you feeling?",
        border_color=PRIMARY_COLOR,
        filled=True,
        expand=True
    )

    notes_field = ft.TextField(
        label="Any notes? (optional)",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_color=PRIMARY_COLOR,
        filled=True
    )

    def submit_mood(e):
        if not mood_dropdown.value:
            show_snackbar("Please select a mood", is_error=True)
            return
            
        submit_button.disabled = True
        submit_button.text = "Submitting..."
        page.update()

        try:
            mood = mood_dropdown.value.split(" ")[1]  # Extract mood without emoji
            notes = notes_field.value if notes_field.value else ""
            
            response = httpx.post(
                f"{API_BASE}/mood",
                json={
                    "username": DEFAULT_USER,
                    "mood": mood,
                    "notes": notes
                },
                timeout=10
            )
            
            if response.status_code == 200:
                show_snackbar("Mood tracked successfully!", is_error=False)
                page.go("/")
            else:
                show_snackbar(f"Error: {response.text}", is_error=True)
                
        except Exception as e:
            show_snackbar(f"Error: {str(e)}", is_error=True)
        finally:
            submit_button.disabled = False
            submit_button.text = "Submit"
            page.update()

    def show_snackbar(message: str, is_error: bool):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.RED_400 if is_error else ft.colors.GREEN_400
        )
        page.snack_bar.open = True
        page.update()

    submit_button = ft.FilledButton(
        "Submit",
        on_click=submit_mood,
        width=200,
        height=50
    )

    return ft.View(
        "/mood",
        controls=[
            ft.AppBar(title=ft.Text("Track Your Mood"), bgcolor=PRIMARY_COLOR),
            ft.Text("How are you feeling today?", size=20, weight=ft.FontWeight.BOLD),
            mood_dropdown,
            notes_field,
            submit_button,
            ft.TextButton("Back to Home", on_click=lambda _: page.go("/"))
        ],
        padding=20,
        spacing=20,
        bgcolor=BACKGROUND_COLOR
    )

def journal_view(page: ft.Page):
    journal_field = ft.TextField(
        label="Write your thoughts...",
        multiline=True,
        min_lines=10,
        border_color=PRIMARY_COLOR,
        filled=True
    )

    def save_journal(e):
        if not journal_field.value.strip():
            show_snackbar("Please write something first", is_error=True)
            return
            
        save_button.disabled = True
        save_button.text = "Saving..."
        page.update()

        try:
            response = httpx.post(
                f"{API_BASE}/journal",
                json={
                    "username": DEFAULT_USER,
                    "content": journal_field.value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                show_snackbar("Journal saved!", is_error=False)
                journal_field.value = ""  # Clear field after save
                page.go("/")              # Go to home, which fetches latest journal
            else:
                show_snackbar(f"Error: {response.text}", is_error=True)
                
        except Exception as e:
            show_snackbar(f"Error: {str(e)}", is_error=True)
        finally:
            save_button.disabled = False
            save_button.text = "Save"
            page.update()

    def show_snackbar(message: str, is_error: bool):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.RED_400 if is_error else ft.colors.GREEN_400
        )
        page.snack_bar.open = True
        page.update()

    save_button = ft.FilledButton(
        "Save Entry",
        on_click=save_journal,
        width=200,
        height=50
    )

    return ft.View(
        "/journal",
        controls=[
            ft.AppBar(title=ft.Text("Daily Reflection"), bgcolor=PRIMARY_COLOR),
            ft.Text("Take a moment to reflect on your day", size=20, weight=ft.FontWeight.BOLD),
            journal_field,
            save_button,
            ft.TextButton("Back to Home", on_click=lambda _: page.go("/"))
        ],
        padding=20,
        spacing=20,
        bgcolor=BACKGROUND_COLOR
    )

def main(page: ft.Page):
    page.title = "Mindful Balance"
    page.window_width = 400
    page.window_height = 700
    page.window_resizable = False
    page.bgcolor = BACKGROUND_COLOR
    page.fonts = {
        "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Roboto")

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(home_view(page))
        elif page.route == "/mood":
            page.views.append(mood_view(page))
        elif page.route == "/journal":
            page.views.append(journal_view(page))
        else:
            page.go("/")
            
        page.update()

    page.on_route_change = route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)

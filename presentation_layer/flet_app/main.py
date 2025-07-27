# presentation_layer/flet_app/main.py
import os
import sys

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

import flet as ft
from business_layer.services.user_service import UserService
from business_layer.services.mood_service import MoodService
from data_layer.database.connection import DatabaseConnection
from io import BytesIO
import base64

class LoginApp:
    """Main Flet application for user authentication."""
    
    def __init__(self):
        self.user_service = UserService()
        self.mood_service = MoodService()
        self.current_user = None
        self.average_mood_text = ft.Text("0.0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600)
        self.total_entries_text = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
        self.latest_journal = ""  # <-- Add this line
        self.last_mood_level = None  # Track last mood selected
        
        # Initialize databaseeeeeee
        db = DatabaseConnection()
        db.initialize_database()

    def main(self, page: ft.Page):
        page.title = "MindfulBalance"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1000  # Wider window for dashboard
        page.window_height = 800
        page.window_resizable = False
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Show welcome screen initially
        self.show_welcome_screen(page)

    def show_welcome_screen(self, page: ft.Page):
        """Display the initial welcome screen"""
        page.clean()
        
        # Welcome title
        title = ft.Text(
            "Welcome to MindfulBalance",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        subtitle = ft.Text(
            "Your daily companion for mental wellness",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        # Login button
        login_btn = ft.ElevatedButton(
            "Sign In",
            width=200,
            on_click=lambda e: self.show_login_page(page),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
        )
        
        # Register button
        register_btn = ft.OutlinedButton(
            "Create Account",
            width=200,
            on_click=lambda e: self.show_register_page(page)
        )
        
        # Layout
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PSYCHOLOGY_ALT, size=100, color=ft.Colors.BLUE_600),
                    ft.Container(height=20),
                    title,
                    subtitle,
                    ft.Container(height=40),
                    login_btn,
                    ft.Container(height=10),
                    register_btn,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLUE_GREY_300,
                    offset=ft.Offset(0, 0)
                )
            )
        )
        
        page.update()

    def show_login_page(self, page: ft.Page):
        """Display the login page."""
        page.clean()
        
        # Title
        title = ft.Text(
            "Welcome to MindfulBalance",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        subtitle = ft.Text(
            "Sign in to your account",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        # Input fields
        self.username_field = ft.TextField(
            label="Username or Email",
            width=300,
            prefix_icon=ft.Icons.PERSON
        )
        
        self.password_field = ft.TextField(
            label="Password",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )
        
        # Error message display
        self.error_text = ft.Text(
            "",
            color=ft.Colors.RED_400,
            size=12
        )
        
        # Login button
        login_btn = ft.ElevatedButton(
            "Sign In",
            width=300,
            on_click=lambda e: self.handle_login(page),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
        )
        
        # Register link
        register_link = ft.TextButton(
            "Don't have an account? Sign up",
            on_click=lambda e: self.show_register_page(page),
            style=ft.ButtonStyle(color=ft.Colors.BLUE_600)
        )
        
        # Layout
        page.add(
            ft.Container(
                content=ft.Column([
                    title,
                    subtitle,
                    ft.Container(height=20),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    ft.Container(height=10),
                    login_btn,
                    register_link
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLUE_GREY_300,
                    offset=ft.Offset(0, 0)
                )
            )
        )
        
        page.update()
    
    def show_register_page(self, page: ft.Page):
        """Display the registration page."""
        page.clean()
        
        # Title
        title = ft.Text(
            "Create Account",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_700
        )
        
        subtitle = ft.Text(
            "Join our mental health community",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        # Input fields
        self.reg_username_field = ft.TextField(
            label="Username",
            width=300,
            prefix_icon=ft.Icons.PERSON,
            helper_text="3-20 characters, letters, numbers, underscore only"
        )
        
        self.reg_email_field = ft.TextField(
            label="Email",
            width=300,
            prefix_icon=ft.Icons.EMAIL
        )
        
        self.reg_password_field = ft.TextField(
            label="Password",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            helper_text="Minimum 6 characters"
        )
        
        self.reg_confirm_password_field = ft.TextField(
            label="Confirm Password",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )
        
        # Error message display
        self.reg_error_text = ft.Text(
            "",
            color=ft.Colors.RED_400,
            size=12
        )
        
        # Register button
        register_btn = ft.ElevatedButton(
            "Create Account",
            width=300,
            on_click=lambda e: self.handle_register(page),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            )
        )
        
        # Back to login link
        login_link = ft.TextButton(
            "Already have an account? Sign in",
            on_click=lambda e: self.show_login_page(page),
            style=ft.ButtonStyle(color=ft.Colors.BLUE_600)
        )
        
        # Layout
        page.add(
            ft.Container(
                content=ft.Column([
                    title,
                    subtitle,
                    ft.Container(height=20),
                    self.reg_username_field,
                    self.reg_email_field,
                    self.reg_password_field,
                    self.reg_confirm_password_field,
                    self.reg_error_text,
                    ft.Container(height=10),
                    register_btn,
                    login_link
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLUE_GREY_300,
                    offset=ft.Offset(0, 0)
                )
            )
        )
        
        page.update()
    
    def handle_login(self, page: ft.Page):
        """Handle login form submission."""
        username_or_email = self.username_field.value
        password = self.password_field.value
        
        success, message, user = self.user_service.authenticate_user(username_or_email, password)
        
        if success:
            self.current_user = user
            self.show_dashboard(page)
        else:
            self.error_text.value = message
            page.update()

    def handle_register(self, page: ft.Page):
        """Handle registration form submission."""
        username = self.reg_username_field.value
        email = self.reg_email_field.value
        password = self.reg_password_field.value
        confirm_password = self.reg_confirm_password_field.value
        
        # Check if passwords match
        if password != confirm_password:
            self.reg_error_text.value = "Passwords do not match"
            page.update()
            return
        
        success, message, user = self.user_service.register_user(username, email, password)
        
        if success:
            # Show success message and redirect to login
            self.show_success_page(page, "Account created successfully! Please sign in.")
        else:
            self.reg_error_text.value = message
            page.update()
    
    def show_success_page(self, page: ft.Page, message: str):
        """Show success message and redirect to login."""
        page.clean()
        
        success_text = ft.Text(
            message,
            size=16,
            color=ft.Colors.GREEN_600,
            text_align=ft.TextAlign.CENTER
        )
        
        login_btn = ft.ElevatedButton(
            "Go to Login",
            on_click=lambda e: self.show_login_page(page),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
        )
        
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=50),
                    ft.Container(height=20),
                    success_text,
                    ft.Container(height=20),
                    login_btn
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLUE_GREY_300,
                    offset=ft.Offset(0, 0)
                )
            )
        )
        
        page.update()
    
    def show_dashboard(self, page: ft.Page):
        """Show main dashboard after successful login."""
        page.clean()
        
        # Header with welcome and logout
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        f"Welcome back, {self.current_user.username}!",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700
                    ),
                    ft.ElevatedButton(
                        "Logout",
                        on_click=lambda e: self.logout(page),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.RED_600,
                            color=ft.Colors.WHITE
                        )
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20
        )

        # Mood tracking section
        mood_section = self.create_mood_section(page)
        
        # Stats section
        stats_section = self.create_stats_section()
        
        # Journal display section
        journal_display = ft.Container(
            content=ft.Column([
                ft.Text("Latest Journal Entry", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                ft.Text(self.latest_journal or "No journal entry yet.", size=14, color=ft.Colors.GREY_700)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.AMBER_50,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0)
            )
        )

        # Add all sections to page
        page.add(
            header,
            ft.Container(height=20),
            mood_section,
            ft.Container(height=20),
            journal_display,  # <-- Add this line
            ft.Container(height=20),
            stats_section
        )
        
        page.update()

    def create_mood_section(self, page: ft.Page):
        """Create the mood tracking section"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "How are you feeling today?",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700
                ),
                ft.Container(height=20),
                ft.Row([
                    self.create_mood_button("😢", "Very Bad", 1, page),
                    self.create_mood_button("😕", "Not Great", 3, page),
                    self.create_mood_button("😐", "Okay", 5, page),
                    self.create_mood_button("🙂", "Good", 7, page),
                    self.create_mood_button("😊", "Great", 10, page),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_300,
                offset=ft.Offset(0, 0)
            )
        )

    def create_mood_button(self, emoji: str, text: str, level: int, page: ft.Page):
        """Create a mood selection button"""
        return ft.ElevatedButton(
            content=ft.Column([
                ft.Text(emoji, size=30),
                ft.Text(text, size=12)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            on_click=lambda e: self.log_mood(level, page),
            style=ft.ButtonStyle(
                padding=20,
                bgcolor=ft.Colors.WHITE,
                color=ft.Colors.BLUE_700
            )
        )

    def create_stats_section(self):
        """Create the statistics section"""
        # Get stats
        mood_stats = self.mood_service.get_mood_statistics(self.current_user.user_id)
        self.average_mood_text.value = f"{mood_stats['average_mood']:.1f}"
        self.total_entries_text.value = str(mood_stats['total_entries'])
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Your Mood Statistics",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700
                ),
                ft.Container(height=10),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Average Mood", size=16),
                            self.average_mood_text
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=20,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=10,
                        width=200
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Total Entries", size=16),
                            self.total_entries_text
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=20,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10,
                        width=200
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_300,
                offset=ft.Offset(0, 0)
            )
        )

    def log_mood(self, mood_level: int, page: ft.Page):
        """Log user's mood and update statistics in real-time."""
        if not self.current_user:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please log in first"),
                bgcolor=ft.Colors.RED_600
            )
            page.update()
            return

        self.last_mood_level = mood_level  # Store the last mood selected

        success, message, stats = self.mood_service.log_mood(
            self.current_user.user_id,
            mood_level
        )

        if success and stats:
            self.average_mood_text.value = f"{stats['average_mood']:.1f}"
            self.total_entries_text.value = str(stats['total_entries'])
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Mood logged successfully!"),
                bgcolor=ft.Colors.GREEN_600
            )
            self.show_hello_dialog(page)
            page.update()
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.RED_600
            )
            page.update()

    def logout(self, page: ft.Page):
        """Handle user logout."""
        self.current_user = None
        page.window_width = 400
        page.window_height = 500
        self.show_welcome_screen(page)

    def show_hello_dialog(self, page: ft.Page):
        """Show a dialog window that asks about creating a journal."""
        def close_dialog(e):
            page.dialog.open = False
            page.update()

        def show_journal_input(e):
            page.dialog.open = False
            page.update()
            self.show_journal_textbox(page)

        dialog = ft.AlertDialog(
            title=ft.Text("Do you want to create a journal?"),
            actions=[
                ft.TextButton("Yes", on_click=show_journal_input),
                ft.TextButton("No", on_click=close_dialog)
            ],
            open=True
        )
        page.dialog = dialog
        if dialog not in page.controls:
            page.controls.append(dialog)
        page.update()

    def show_journal_textbox(self, page: ft.Page):
        """Show a dialog with a text box for writing a journal entry."""
        journal_field = ft.TextField(
            label="Write your journal entry...",
            multiline=True,
            width=400,
            min_lines=5,
            max_lines=10
        )

        def save_journal(e):
            self.latest_journal = journal_field.value  # Save the journal text
            page.dialog.open = False
            page.update()
            self.show_dashboard(page)  # Refresh dashboard to show the journal
            # Show mental tip after dashboard refresh
            tip = self.get_mental_tip(self.last_mood_level)
            tip_dialog = ft.AlertDialog(
                title=ft.Text("Mental Health Tip"),
                content=ft.Text(tip),
                actions=[ft.TextButton("OK", on_click=lambda e: self.close_tip_dialog(page))],
                open=True
            )
            page.dialog = tip_dialog
            if tip_dialog not in page.controls:
                page.controls.append(tip_dialog)
            page.update()

        def close_journal(e):
            page.dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Journal Entry"),
            content=journal_field,
            actions=[
                ft.TextButton("Save", on_click=save_journal),
                ft.TextButton("Cancel", on_click=close_journal)
            ],
            open=True
        )
        page.dialog = dialog
        if dialog not in page.controls:
            page.controls.append(dialog)
        page.update()

    def close_tip_dialog(self, page: ft.Page):
        page.dialog.open = False
        page.update()

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

def main(page: ft.Page):
    app = LoginApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)
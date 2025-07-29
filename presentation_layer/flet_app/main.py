# presentation_layer/flet_app/main.py
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

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

    def create_mood_plots(self, page: ft.Page):
        """Create and display mood trend plots using matplotlib."""
        if not self.current_user:
            return

        try:
            print("Starting to create mood plots...")  # Debug
            
            # Get mood history for the last 30 days
            mood_history = self.mood_service.get_user_mood_history(self.current_user.user_id, 30)
            print(f"Retrieved {len(mood_history)} mood entries")  # Debug

            if not mood_history:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("No mood data available for plotting"),
                    bgcolor=ft.Colors.ORANGE_600
                )
                page.snack_bar.open = True
                page.update()
                return

            # Prepare data for plotting
            dates = []
            mood_levels = []
            journal_counts = {}

            for mood in mood_history:
                if mood.timestamp:
                    # Handle different timestamp formats
                    if isinstance(mood.timestamp, str):
                        try:
                            timestamp = datetime.fromisoformat(mood.timestamp)
                        except:
                            timestamp = datetime.strptime(mood.timestamp, '%Y-%m-%d %H:%M:%S')
                    else:
                        timestamp = mood.timestamp
                    
                    date = timestamp.date()
                    dates.append(date)
                    mood_levels.append(mood.mood_level)

                    # Count journal entries (notes)
                    if mood.notes and mood.notes.strip():
                        journal_counts[date] = journal_counts.get(date, 0) + 1

            if not dates:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("No valid mood data for plotting"),
                    bgcolor=ft.Colors.ORANGE_600
                )
                page.snack_bar.open = True
                page.update()
                return

            print(f"Processed {len(dates)} data points for plotting")  # Debug

            # Create the plots
            plt.style.use('default')  # Ensure we're using default style
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
            fig.suptitle(f'Mental Health Dashboard - {self.current_user.username}', fontsize=16, fontweight='bold')

            # Plot 1: Mood Trends
            ax1.plot(dates, mood_levels, marker='o', linestyle='-', linewidth=2, markersize=6, color='#2E86AB')
            ax1.set_title('Mood Trends Over Time', fontweight='bold')
            ax1.set_ylabel('Mood Level (1-10)')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 11)

            # Add mood level labels
            mood_labels = {1: 'Terrible', 3: 'Bad', 5: 'Okay', 7: 'Good', 10: 'Excellent'}
            for level, label in mood_labels.items():
                ax1.axhline(y=level, color='gray', linestyle='--', alpha=0.3)
                ax1.text(min(dates), level, label, fontsize=8, alpha=0.7)

            # Plot 2: Journaling Frequency
            if journal_counts:
                journal_dates = list(journal_counts.keys())
                journal_freq = list(journal_counts.values())
                ax2.bar(journal_dates, journal_freq, color='#A23B72', alpha=0.7)
                ax2.set_title('Journaling Frequency', fontweight='bold')
                ax2.set_ylabel('Journal Entries')
            else:
                ax2.text(0.5, 0.5, 'No journal entries available', 
                        transform=ax2.transAxes, ha='center', va='center', fontsize=12)
                ax2.set_title('Journaling Frequency', fontweight='bold')
                ax2.set_ylabel('Journal Entries')

            # Plot 3: Wellness Score (7-day rolling average)
            if len(mood_levels) >= 7:
                wellness_scores = []
                wellness_dates = []

                for i in range(6, len(mood_levels)):
                    window_moods = mood_levels[i-6:i+1]
                    wellness_score = sum(window_moods) / len(window_moods)
                    wellness_scores.append(wellness_score)
                    wellness_dates.append(dates[i])

                ax3.fill_between(wellness_dates, wellness_scores, alpha=0.3, color='#F18F01')
                ax3.plot(wellness_dates, wellness_scores, color='#F18F01', linewidth=2)
                ax3.set_title('Wellness Score (7-day Average)', fontweight='bold')
                ax3.set_ylabel('Wellness Score')
                ax3.set_ylim(0, 11)
            else:
                ax3.text(0.5, 0.5, 'Need at least 7 mood entries for wellness score', 
                        transform=ax3.transAxes, ha='center', va='center', fontsize=12)
                ax3.set_title('Wellness Score (7-day Average)', fontweight='bold')
                ax3.set_ylabel('Wellness Score')

            # Format x-axis for all plots
            for ax in [ax1, ax2, ax3]:
                if len(dates) > 1:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            plt.tight_layout()

            # Save plot as image
            plot_dir = os.path.dirname(__file__)
            plot_path = os.path.join(plot_dir, 'mood_plot.png')
            print(f"Saving plot to: {plot_path}")  # Debug
            
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()  # Close to free memory

            print("Plot saved successfully, showing dialog...")  # Debug

            # Show a nice popup dialog
            def close_dialog(e):
                page.dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Analytics Created!", size=18, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    "Successfully created a Matplotlib graph! You can view it in the app or check your local folder for 'mood_plot.png'.",
                    size=16,
                    color=ft.Colors.BLUE_700
                ),
                actions=[ft.TextButton("OK", on_click=close_dialog)],
                open=True
            )
            page.dialog = dialog
            if dialog not in page.controls:
                page.controls.append(dialog)
            page.update()

            # Optionally, still show the plot in-app as before:
            self.show_plot_dialog(page, plot_path)

        except Exception as e:
            print(f"Error creating plots: {str(e)}")  # Debug
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error creating plots: {str(e)}"),
                bgcolor=ft.Colors.RED_600
            )
            page.snack_bar.open = True
            page.update()

    def show_plot_dialog(self, page: ft.Page, plot_path: str):
        """Display the matplotlib plot in a dialog."""
        try:
            print(f"Showing plot dialog for: {plot_path}")  # Debug

            # Check if file exists
            if not os.path.exists(plot_path):
                raise FileNotFoundError(f"Plot file not found: {plot_path}")

            plot_image = ft.Image(
                src=plot_path,
                width=800,
                height=600,
                fit=ft.ImageFit.CONTAIN
            )

            def close_plot(e):
                page.dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Your Mental Health Analytics", size=18, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=plot_image,
                    width=800,
                    height=600
                ),
                actions=[
                    ft.TextButton("Close", on_click=close_plot)
                ],
                open=True
            )

            page.dialog = dialog
            page.update()

        except Exception as e:
            print(f"Error displaying plot: {str(e)}")  # Debug
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error displaying plot: {str(e)}"),
                bgcolor=ft.Colors.RED_600
            )
            page.snack_bar.open = True
            page.update()

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

        # Analytics button
        analytics_btn = ft.ElevatedButton(
    "📊 View Analytics",
    on_click=lambda e: self.create_mood_plots(page),
    style=ft.ButtonStyle(
        bgcolor=ft.Colors.PURPLE_600,
        color=ft.Colors.WHITE
    )
)

        # Mood tracking section
        mood_section = self.create_mood_section(page)
        
        # Stats section
        stats_section = self.create_stats_section()
        
        # Journal history button
        journal_history_btn = ft.ElevatedButton(
            "View Journal History",
            on_click=lambda e: self.show_journal_history(page),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.AMBER_700,
                color=ft.Colors.WHITE
            )
        )

        # Add all sections to page
        page.add(
            header,
            ft.Container(height=10),
            analytics_btn,
            ft.Container(height=20),
            mood_section,
            ft.Container(height=20),
            journal_history_btn,  # <-- Add this line
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
            import datetime
            journal_text = journal_field.value.strip()
            if journal_text:
                # Save journal entry to file
                file_path = os.path.join(os.path.dirname(__file__), "journal_history.txt")
                with open(file_path, "a", encoding="utf-8") as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp}: {journal_text}\n")
            page.dialog.open = False
            page.update()
            # Show mental tip after closing journal dialog
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

    def show_journal_history(self, page: ft.Page):
        """Show a dialog with the history of journal entries from file."""
        file_path = os.path.join(os.path.dirname(__file__), "journal_history.txt")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            if lines:
                content = ft.Column(
                    [ft.Text(entry, size=14) for entry in lines],
                    scroll="auto",
                    width=400,
                    height=400
                )
            else:
                content = ft.Text("No journal entries found.", size=14)
        else:
            content = ft.Text("No journal entries found.", size=14)

        dialog = ft.AlertDialog(
            title=ft.Text("Journal History"),
            content=content,
            actions=[ft.TextButton("Close", on_click=lambda e: self.close_tip_dialog(page))],
            open=True
        )
        page.dialog = dialog
        if dialog not in page.controls:
            page.controls.append(dialog)
        page.update()

def main(page: ft.Page):
    app = LoginApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)
# presentation_layer/flet_app/main.py
import os
import sys

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

import flet as ft
from business_layer.services.user_service import UserService
from data_layer.database.connection import DatabaseConnection

class LoginApp:
    """Main Flet application for user authentication."""
    
    def __init__(self):
        self.user_service = UserService()
        self.current_user = None
        
        # Initialize database
        db = DatabaseConnection()
        db.initialize_database()
    
    def main(self, page: ft.Page):
        """Main application entry point."""
        page.title = "MindfulBalance - Login"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 400
        page.window_height = 500
        page.window_resizable = False
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Show login page initially
        self.show_login_page(page)
    
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
        
        welcome_text = ft.Text(
            f"Welcome, {self.current_user.username}!",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        subtitle = ft.Text(
            "Community Mental Health Tracker Dashboard",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        logout_btn = ft.ElevatedButton(
            "Logout",
            on_click=lambda e: self.logout(page),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE
            )
        )
        
        # Placeholder for future dashboard content
        dashboard_content = ft.Text(
            "Dashboard content will go here...\n"
            "• Mood tracking\n"
            "• Journal entries\n"
            "• Analytics\n"
            "• Coping strategies",
            size=14,
            color=ft.Colors.GREY_700
        )
        
        page.add(
            ft.Container(
                content=ft.Column([
                    welcome_text,
                    subtitle,
                    ft.Container(height=30),
                    dashboard_content,
                    ft.Container(height=30),
                    logout_btn
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
    
    def logout(self, page: ft.Page):
        """Handle user logout."""
        self.current_user = None
        self.show_login_page(page)

def main(page: ft.Page):
    app = LoginApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)
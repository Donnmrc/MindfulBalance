import flet as ft
import httpx
from constants import API_BASE, PRIMARY_COLOR, BACKGROUND_COLOR, SECONDARY_COLOR

def login_view(page: ft.Page):
    username_field = ft.TextField(
        label="Username",
        border_color=PRIMARY_COLOR,
        filled=True,
        expand=True
    )
    
    password_field = ft.TextField(
        label="Password",
        border_color=PRIMARY_COLOR,
        filled=True,
        password=True,
        can_reveal_password=True,
        expand=True
    )

    def show_snackbar(message: str, is_error: bool = False):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.RED_400 if is_error else ft.colors.GREEN_400
        )
        page.snack_bar.open = True
        page.update()

    async def handle_login(e):
        if not username_field.value or not password_field.value:
            show_snackbar("Please fill in all fields", is_error=True)
            return

        login_button.disabled = True
        login_button.text = "Logging in..."
        page.update()

        try:
            response = await httpx.post(
                f"{API_BASE}/login",
                json={
                    "username": username_field.value,
                    "password": password_field.value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                show_snackbar("Login successful!")
                page.client_storage.set("username", username_field.value)
                page.go("/")
            else:
                show_snackbar(f"Login failed: {response.json()['detail']}", is_error=True)
                
        except Exception as e:
            show_snackbar(f"Error: {str(e)}", is_error=True)
        finally:
            login_button.disabled = False
            login_button.text = "Login"
            page.update()

    login_button = ft.FilledButton(
        "Login",
        on_click=handle_login,
        width=200,
        height=50
    )

    return ft.View(
        "/login",
        [
            ft.AppBar(title=ft.Text("Login"), bgcolor=PRIMARY_COLOR),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Welcome Back!", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Please login to continue", size=16),
                        username_field,
                        password_field,
                        login_button,
                        ft.TextButton(
                            "Don't have an account? Register",
                            on_click=lambda _: page.go("/register")
                        )
                    ],
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20,
                alignment=ft.alignment.center
            )
        ],
        padding=20,
        bgcolor=BACKGROUND_COLOR,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

def register_view(page: ft.Page):
    username_field = ft.TextField(
        label="Username",
        border_color=PRIMARY_COLOR,
        filled=True,
        expand=True
    )
    
    password_field = ft.TextField(
        label="Password",
        border_color=PRIMARY_COLOR,
        filled=True,
        password=True,
        can_reveal_password=True,
        expand=True
    )
    
    confirm_password_field = ft.TextField(
        label="Confirm Password",
        border_color=PRIMARY_COLOR,
        filled=True,
        password=True,
        can_reveal_password=True,
        expand=True
    )

    def show_snackbar(message: str, is_error: bool = False):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.RED_400 if is_error else ft.colors.GREEN_400
        )
        page.snack_bar.open = True
        page.update()

    async def handle_register(e):
        if not all([username_field.value, password_field.value, confirm_password_field.value]):
            show_snackbar("Please fill in all fields", is_error=True)
            return

        if password_field.value != confirm_password_field.value:
            show_snackbar("Passwords don't match", is_error=True)
            return

        register_button.disabled = True
        register_button.text = "Registering..."
        page.update()

        try:
            response = await httpx.post(
                f"{API_BASE}/register",
                json={
                    "username": username_field.value,
                    "password": password_field.value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                show_snackbar("Registration successful!")
                page.go("/login")
            else:
                show_snackbar(f"Registration failed: {response.json()['detail']}", is_error=True)
                
        except Exception as e:
            show_snackbar(f"Error: {str(e)}", is_error=True)
        finally:
            register_button.disabled = False
            register_button.text = "Register"
            page.update()

    register_button = ft.FilledButton(
        "Register",
        on_click=handle_register,
        width=200,
        height=50
    )

    return ft.View(
        "/register",
        [
            ft.AppBar(title=ft.Text("Register"), bgcolor=PRIMARY_COLOR),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Create Account", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Sign up to get started", size=16),
                        username_field,
                        password_field,
                        confirm_password_field,
                        register_button,
                        ft.TextButton(
                            "Already have an account? Login",
                            on_click=lambda _: page.go("/login")
                        )
                    ],
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20,
                alignment=ft.alignment.center
            )
        ],
        padding=20,
        bgcolor=BACKGROUND_COLOR,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
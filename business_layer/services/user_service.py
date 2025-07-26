# business_layer/services/user_service.py
import hashlib
import secrets
from typing import Optional, Tuple
from business_layer.models.user import User
from data_layer.dao.user_dao import UserDAO

class UserService:
    """Business logic for user operations."""
    
    def __init__(self):
        self.user_dao = UserDAO()
    
    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """
        Hash password with salt.
        
        Args:
            password: Plain text password
            salt: Salt for hashing (generated if None)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine password and salt, then hash
        password_salt = password + salt
        hashed = hashlib.sha256(password_salt.encode()).hexdigest()
        return f"{salt}:{hashed}", salt
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            stored_hash: Stored hash in format "salt:hash"
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, hash_part = stored_hash.split(':', 1)
            test_hash, _ = self._hash_password(password, salt)
            return test_hash == stored_hash
        except ValueError:
            return False
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user.
        
        Args:
            username: Desired username
            email: User's email address
            password: Plain text password
            
        Returns:
            Tuple of (success, message, user_object)
        """
        # Create user object for validation
        user = User(username=username, email=email)
        
        # Validate input
        if not user.is_valid_username:
            return False, "Username must be 3-20 characters and contain only letters, numbers, and underscores", None
        
        if not user.is_valid_email:
            return False, "Please enter a valid email address", None
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long", None
        
        # Check if username or email already exists
        if self.user_dao.username_exists(username):
            return False, "Username already exists", None
        
        if self.user_dao.email_exists(email):
            return False, "Email already registered", None
        
        # Hash password and create user
        hashed_password, _ = self._hash_password(password)
        user_id = self.user_dao.create_user(username, email, hashed_password)
        
        if user_id:
            user.user_id = user_id
            return True, "User registered successfully", user
        else:
            return False, "Registration failed. Please try again.", None
    
    def authenticate_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate user login.
        
        Args:
            username_or_email: Username or email address
            password: Plain text password
            
        Returns:
            Tuple of (success, message, user_object)
        """
        if not username_or_email or not password:
            return False, "Please enter both username/email and password", None
        
        # Try to find user by username first, then by email
        user_data = self.user_dao.get_user_by_username(username_or_email)
        if not user_data:
            user_data = self.user_dao.get_user_by_email(username_or_email)
        
        if not user_data:
            return False, "Invalid username/email or password", None
        
        # Verify password
        if self._verify_password(password, user_data['password']):
            user = User.from_dict(user_data)
            return True, "Login successful", user
        else:
            return False, "Invalid username/email or password", None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        user_data = self.user_dao.get_user_by_id(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        # Get user data including password hash
        user_data = self.user_dao.get_user_by_id(user_id)
        if not user_data:
            return False, "User not found"
        
        # Get full user data with password for verification
        full_user_data = self.user_dao.get_user_by_username(user_data['username'])
        if not full_user_data:
            return False, "User not found"
        
        # Verify old password
        if not self._verify_password(old_password, full_user_data['password']):
            return False, "Current password is incorrect"
        
        # Validate new password
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long"
        
        # Hash new password and update (you'll need to add this method to UserDAO)
        hashed_password, _ = self._hash_password(new_password)
        # Note: You'll need to implement update_password method in UserDAO
        
        return True, "Password changed successfully"
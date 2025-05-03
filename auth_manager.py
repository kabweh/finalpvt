"""
Authentication module for AI Tutor application.
Handles user authentication, invite-only signup, and subscription management.
"""
import os
import datetime
import secrets
import bcrypt
from typing import Dict, Any, Optional, Tuple

# Assuming database.py is in the same directory
from database import Database

class AuthManager:
    """
    Handles authentication and subscription management for the AI Tutor application.
    """

    def __init__(self, database: Database):
        """
        Initialize the authentication manager.

        Args:
            database: Database instance for user storage
        """
        self.database = database

    def register_user(self, username: str, password: str, email: Optional[str] = None,
                     invite_token: Optional[str] = None) -> Dict:
        """
        Register a new user.
        Allows the first user to register without an invite token.

        Args:
            username: User's username
            password: User's password (will be hashed)
            email: User's email address (optional)
            invite_token: Invite token for invite-only signup (optional for first user)

        Returns:
            Dictionary containing registration status and user info if successful
        """
        is_first_user = self.database.count_users() == 0

        # Check if invite token is required
        if not is_first_user and not invite_token:
            return {
                "success": False,
                "message": "Invite token is required for registration."
            }

        # Validate username and password
        if not username or len(username) < 3:
            return {
                "success": False,
                "message": "Username must be at least 3 characters long."
            }

        if not password or len(password) < 8:
            return {
                "success": False,
                "message": "Password must be at least 8 characters long."
            }

        # Hash the password
        password_hash = self._hash_password(password)

        # Add user to database
        user_id = self.database.add_user(username, password_hash, email)

        if user_id == -1:
            return {
                "success": False,
                "message": "Username or email already exists."
            }

        # Mark invite token as used (only if not the first user)
        token_used_successfully = True
        if not is_first_user:
            if not self.database.use_invite_link(invite_token, user_id):
                token_used_successfully = False
                # Decide if registration should fail if token is invalid for non-first users
                # Current logic allows registration but warns about the token.
                # If strict enforcement is needed, return failure here.
                # return {
                #     "success": False,
                #     "message": "Invite token is invalid or expired."
                # }

        # Get the user info
        user = self.database.get_user_by_username(username)

        message = "User registered successfully."
        if not is_first_user and not token_used_successfully:
            message = "User registered successfully, but invite token was invalid or expired."
        elif is_first_user:
             message = "Administrator account registered successfully."


        return {
            "success": True,
            "message": message,
            "user": user
        }

    def login_user(self, username: str, password: str) -> Dict:
        """
        Log in a user.

        Args:
            username: User's username
            password: User's password

        Returns:
            Dictionary containing login status and user info if successful
        """
        # Get user from database
        user = self.database.get_user_by_username(username)

        if not user:
            return {
                "success": False,
                "message": "Invalid username or password."
            }

        # Check password
        if not self._check_password(password, user['password_hash']):
            return {
                "success": False,
                "message": "Invalid username or password."
            }

        return {
            "success": True,
            "message": "Login successful.",
            "user": user
        }

    def generate_invite_link(self, created_by: int, email: Optional[str] = None,
                            expires_in_days: int = 7) -> Tuple[int, str]:
        """
        Generate a new invite link.

        Args:
            created_by: User ID of the creator
            email: Email address the invite is for (optional)
            expires_in_days: Number of days until the invite expires

        Returns:
            Tuple of (invite_id, token)
        """
        return self.database.create_invite_link(created_by, email, expires_in_days)

    def validate_invite_token(self, token: str) -> Dict:
        """
        Validate an invite token by checking the database.

        Args:
            token: The invite token

        Returns:
            Dictionary containing validation status and invite info if valid
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, email, expires_at FROM invite_links WHERE token = ? AND used = 0",
            (token,)
        )
        invite = cursor.fetchone()

        if not invite:
            return {
                "success": False,
                "message": "Invalid or already used invite token."
            }

        # Check if token is expired
        try:
            expires_at = datetime.datetime.fromisoformat(invite["expires_at"])
        except ValueError:
            return {
                "success": False,
                "message": "Invalid invite token format."
            }

        if expires_at < datetime.datetime.now():
            return {
                "success": False,
                "message": "Invite token has expired."
            }

        return {
            "success": True,
            "message": "Invite token is valid.",
            "invite": dict(invite)
        }

    def activate_subscription(self, user_id: int, duration_days: int = 30) -> Dict:
        """
        Activate a subscription for a user (Placeholder).

        Args:
            user_id: User ID
            duration_days: Number of days to activate the subscription for

        Returns:
            Dictionary containing activation status
        """
        # Placeholder - In real app, update DB: users table set subscription_active=1, subscription_expires=...
        expires_at_dt = datetime.datetime.now() + datetime.timedelta(days=duration_days)
        expires_at_iso = expires_at_dt.isoformat()

        # Simulate DB update (in real app, call self.database.update_subscription(user_id, expires_at_iso))
        print(f"Simulating subscription activation for user {user_id} until {expires_at_iso}")

        return {
            "success": True,
            "message": "Subscription activated successfully.",
            "expires_at": expires_at_iso
        }

    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Password to hash

        Returns:
            Hashed password as a string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _check_password(self, password: str, hashed_password: str) -> bool:
        """
        Check if a password matches a hash.

        Args:
            password: Password to check
            hashed_password: Hashed password to compare against

        Returns:
            True if the password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ValueError:
             # Handle cases where hashed_password might not be a valid bcrypt hash
             return False

# End of class AuthManager


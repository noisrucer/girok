"""
Authentication handler for local session management.
Automatically handles local user provisioning.
"""
import os

from girok.constants import APP_DIR, CONFIG_PATH
from girok.database.db import create_user, get_user_by_email, init_database
from girok.utils.json_utils import read_json, update_json, write_json


class AuthHandler:

    @classmethod
    def init(cls) -> None:
        """Initialize application directory, config, and database."""
        # Ensure application directory exists
        if not os.path.isdir(APP_DIR):
            os.makedirs(APP_DIR)

        # Ensure config.json exists
        if not os.path.exists(CONFIG_PATH):
            write_json(CONFIG_PATH, {})

        # Initialize database schema
        init_database()
        
        # Ensure default user exists
        cls._ensure_default_user()

    @classmethod
    def _ensure_default_user(cls) -> None:
        """Ensure a default local user exists and is set in config."""
        default_email = "local@girok"
        
        user = get_user_by_email(default_email)
        if not user:
            # Create default user
            user_id = create_user(default_email, "local_hash")
        else:
            user_id = user["id"]
            
        # Update config with this user_id
        update_json(CONFIG_PATH, {"user_id": user_id})

    @classmethod
    def is_logged_in(cls) -> bool:
        """Always returns True for local offline mode."""
        return True

    @classmethod
    def get_user_id(cls) -> int:
        """Get the current local user's ID."""
        # Ensure we are initialized
        if not os.path.exists(CONFIG_PATH):
            cls.init()
            
        cfg = read_json(CONFIG_PATH)
        if "user_id" not in cfg:
            cls.init() # Retry init
            cfg = read_json(CONFIG_PATH)
            
        return cfg["user_id"]

    # Keep get_access_token as alias for compatibility
    @classmethod
    def get_access_token(cls) -> int:
        """Alias for get_user_id for backward compatibility."""
        return cls.get_user_id()

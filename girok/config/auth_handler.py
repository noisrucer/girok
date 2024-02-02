import os

import girok.api.auth as auth_api
from girok.constants import APP_DIR, CONFIG_PATH
from girok.utils.json_utils import read_json, update_json, write_json


class AuthHandler:
    
    @classmethod
    def init(cls) -> None:
        # Ensure application directory exists
        if not os.path.isdir(APP_DIR):
            os.makedirs(APP_DIR)

        # Ensure config.json exists
        if not os.path.exists(CONFIG_PATH):
            write_json(CONFIG_PATH, {})

    @classmethod
    def is_logged_in(cls) -> bool:
        # Ensure config.json exists
        if not is_config_exist():
            return False

        # Ensure access_token is present
        cfg = read_json(CONFIG_PATH)
        if "access_token" not in cfg:
            return False

        # Ensure access_token is valid
        access_token = cfg["access_token"]
        return auth_api.verify_access_token(access_token)

    @classmethod
    def login(cls, access_token: str) -> None:
        update_json(CONFIG_PATH, {"access_token": access_token})

    @classmethod
    def logout(cls) -> None:
        cfg = read_json(CONFIG_PATH)
        if "access_token" in cfg:
            del cfg["access_token"]
            write_json(CONFIG_PATH, cfg)

    @classmethod
    def get_access_token(cls) -> str:
        cfg = read_json(CONFIG_PATH)
        if "access_token" not in cfg:
            raise ValueError("Access token not found.")
        return cfg["access_token"]


def is_config_exist():
    return os.path.exists(CONFIG_PATH)

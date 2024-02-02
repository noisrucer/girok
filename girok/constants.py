import os
from enum import Enum

import typer

# App Config
# BASE_URL = "http://girok-server-balancer-1565927748.ap-northeast-1.elb.amazonaws.com:8080/"
BASE_URL = "http://localhost:8080/api/v1/"
APP_NAME = "girok"
APP_DIR = typer.get_app_dir(APP_NAME)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
VERSION = "0.2.0"


# Commands
class CommandName:

    # Utility Commands
    VERSION = "version"

    # Auth Commands
    REGISTER = "register"
    LOGIN = "login"
    LOGOUT = "logout"


# Terminal display color
class DisplayBoxType(Enum):
    TITLE = ("#000000", "#F6DA75")
    SUCCESS = ("#000000", "#B0D78F")
    ERROR = ("#000000", "#FFAFB0")
    WARNING = ("#000000", "#F2CFA5")

    def __init__(self, text_color_hex: str, bg_color_hex: str):
        self.text_color_hex = text_color_hex
        self.bg_color_hex = bg_color_hex


# Emojis
class Emoji:
    LEFT_ARROW = "⬅"
    CIRCLE = "●"


# Color Pallete
COLOR_PALETTE = {
    "GREYISH_YELLOW": "#F1DB76",
    "LIME": "#E7F8CC",
    "BEIGE": "#E7F8CC",
    "LIGHT_PINK": "#8C0CB",
    "GREYISH_GREEN": "#97C1A9",
    "GREYISH_BLUE": "#B0C1D5",
    "CLOUDY": "#94C7CB",
    "LAVENDER": "#C6C1EA",
    "CORN": "#FFD3B6",
    "MINT": "#B0E7EC",
    "NEON": "#E1E85E",
    "ROLLER_RINK": "#FF9B7B",
    "LIGHT_CHOCO": "#CD9677",
    "THOMAS": "#B19C89",
}

DEFAULT_ITEM_COLOR = "#D7C8B7"

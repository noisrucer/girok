import os
from enum import Enum

import typer

# App Config
# BASE_URL = "http://girok-server-balancer-1565927748.ap-northeast-1.elb.amazonaws.com:8080/"
BASE_URL = "http://localhost:8080/api/v1/"
APP_NAME = "girok"
APP_DIR = typer.get_app_dir(APP_NAME)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
EVENT_IDS_CACHE_PATH = os.path.join(APP_DIR, "event_ids_cache.json")
VERSION = "0.2.0"


# Commands
class CommandName:

    # Utility Commands
    VERSION = "version"

    # Auth Commands
    REGISTER = "register"
    LOGIN = "login"
    LOGOUT = "logout"

    # Category Commands
    COLORS = "colors"

    # Task Commands
    ADD_TASK = "addtask"


# Terminal display color
class DisplayBoxType(Enum):
    TITLE = ("#000000", "#F6DA75")
    SUCCESS = ("#000000", "#B0D78F")
    ERROR = ("#000000", "#FFAFB0")
    WARNING = ("#000000", "#F2CFA5")

    def __init__(self, text_color_hex: str, bg_color_hex: str):
        self.text_color_hex = text_color_hex
        self.bg_color_hex = bg_color_hex


class DisplayArrowType(Enum):
    INFO = "yellow"
    ERROR = "bright_red"


# Emojis
class Emoji:
    LEFT_ARROW = "⬅"
    CIRCLE = "●"


# Color Palette
CATEGORY_COLOR_PALETTE = {
    "GREYISH_YELLOW": "#F1DB76",
    "LIME": "#E7F8CC",
    "BEIGE": "#E7F8CC",
    "LIGHT_PINK": "#E8C0CB",
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
    "PINK": "#F395C7",
}

# Automatic category color assignment order
CATEGORY_COLOR_AUTO_ASSIGNMENT_ORDER = [
    "GREYISH_YELLOW",
    "ROLLER_RINK",
    "GREYISH_BLUE",
    "GREYISH_GREEN",
    "LAVENDER",
    "LIME",
    "LIGHT_CHOCO",
    "NEON",
    "THOMAS",
    "MINT",
    "BEIGE",
    "CLOUDY",
    "CORN",
    "LIGHT_PINK",
    "PINK",
]

DEFAULT_CATEGORY_COLOR = "#808080"

TASK_PRIORITY = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH"}

REPETITION_TYPE = {"daily": "DAILY", "weekly": "WEEKLY", "monthly": "MONTHLY", "yearly": "YEARLY"}

DEFAULT_CATEGORY_TEXT_COLOR = "#D7C8B7"
HIGHLIGHT_CATEGORY_TEXT_COLOR = "#B9D66A"

TABLE_HEADER_TEXT_COLOR = "#D7E1C9"
TABLE_EVENT_NAME_COLOR = "#FAC7C1"
TABLE_DEFAULT_TEXT_COLOR = "#D7C8B7"
TABLE_EVENT_DELETED_COLOR = "#808080"
TABLE_EVENT_HIGHLIGHT_COLOR = "#B1EEC9"
TABLE_DATETIME_COLOR = "#A8CCDC"

EVENT_TREE_CATEGORY_COLOR = "#FAC7C1"
EVENT_TREE_EVENT_COLOR = "#CD9677"
EVENT_TREE_DATETIME_COLOR = "#A8CCDC"
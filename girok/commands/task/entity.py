from dataclasses import dataclass
from typing import List

from girok.constants import CATEGORY_COLOR_PALETTE


@dataclass
class EventDate:
    start_date: str
    start_time: str
    end_date: str
    end_time: str


@dataclass
class Repetition:
    repetition_type: str
    repetition_end_date: str


@dataclass
class Category:
    id: int
    name: str


@dataclass
class Event:
    id: int
    name: str
    color_str: str
    tags: List[str]
    priority: str
    memo: str
    event_date: EventDate
    repetition: Repetition
    category_path: List[Category]

    def __post_init__(self):
        self.color_hex = CATEGORY_COLOR_PALETTE[self.color_str]

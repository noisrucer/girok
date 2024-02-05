import calendar
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

from girok.constants import CATEGORY_COLOR_PALETTE
from girok.utils.time import convert_iso_date_str_to_date_obj


@dataclass
class EventDate:
    start_date: str
    start_time: Optional[str]
    end_date: Optional[str]
    end_time: Optional[str]


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

    def get_all_days_for_month(self, year: int, month: int) -> list[int]:
        """
        1. start_date -> repeat
        2. start_date, start_time -> repeat
        3. start_date, end_date
        4. start_date, start_time, end_date, end_time -> repeat
        """
        month_first_date = datetime(year, month, 1)
        month_last_date = datetime(year, month, calendar.monthrange(year, month)[1])

        start_date = convert_iso_date_str_to_date_obj(self.event_date.start_date)
        end_date = None
        if self.event_date.end_date:
            end_date = convert_iso_date_str_to_date_obj(self.event_date.end_date)

        repetition_type = self.repetition.repetition_type
        repetition_end_date = self.repetition.repetition_end_date

        if repetition_type: # only start_date matters
            if repetition_type == 'DAILY':
                fallin_days: List[int] = []
                start = max(start_date, month_first_date)
                end = month_last_date if not repetition_end_date else min(month_last_date, repetition_end_date)

                return [d for d in range(start.day, end.day + 1)]
            elif repetition_type == 'WEEKLY':
                fallin_days: List[int] = []
                weekday = start_date.weekday()
                diff = (weekday - month_first_date.weekday() + 7) % 7
                month_first_weekday_date = month_first_date + timedelta(days=diff)
                cut_off_date = month_last_date if not repetition_end_date else min(month_last_date, repetition_end_date)

                while month_first_weekday_date <= cut_off_date:
                    fallin_days.append(month_first_weekday_date.day)
                    month_first_weekday_date += timedelta(days=7)

                return fallin_days
            elif repetition_type == 'MONTHLY':
                return [start_date.day]
            elif repetition_type == 'YEARLY':
                return [start_date.day]
            else:
                raise ValueError("Invalid repetition type")
        else:
            if end_date:
                start = max(start_date, month_first_date)
                end = min(end_date, month_last_date)
                return [d for d in range(start.day, end.day + 1)]
            else: # single-day
                return [start_date.day]
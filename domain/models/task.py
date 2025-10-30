from dataclasses import dataclass
from datetime import date
from typing import Optional

from .user import User


@dataclass
class Task:
    id: Optional[int]
    text: str
    creator: User
    done: bool = False
    due_date: Optional[date] = None

    def mark_done(self):
        self.done = True

    def reopen(self):
        self.done = False

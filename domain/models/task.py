from dataclasses import dataclass
from typing import Optional

from .user import User


@dataclass
class Task:
    id: Optional[int]
    text: str
    creator: User
    done: bool = False

    def mark_done(self):
        self.done = True

    def reopen(self):
        self.done = False

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    telegram_id: int

from pydantic import BaseModel, model_validator

from typing import Optional


class CreateTaskDTO(BaseModel):
    user_id: int
    text: str


class TaskCreateRawData(BaseModel):
    user_id: Optional[int] = None
    telegram_id: Optional[int] = None
    text: str

    @model_validator(mode="after")
    def check_user_or_telegram(self):
        if self.user_id is None and self.telegram_id is None:
            raise ValueError("Either user_id or telegram_id must be provided")
        return self

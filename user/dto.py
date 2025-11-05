from pydantic import BaseModel, model_validator

from typing import Optional


class RegisterUserDTO(BaseModel):
    telegram_id: int

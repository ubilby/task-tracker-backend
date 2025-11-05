from pydantic import BaseModel


class RegisterUserDTO(BaseModel):
    telegram_id: int

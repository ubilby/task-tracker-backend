from pydantic import BaseModel

from user.dto import RegisterUserDTO


class UserCreateRequest(RegisterUserDTO):
    ...


class UserResponse(BaseModel):
    id: int
    telegram_id: int

    class ConfigDict:
        from_attributes = True


class DeleteResponse(BaseModel):
    success: bool

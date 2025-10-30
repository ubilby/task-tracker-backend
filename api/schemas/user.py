from pydantic import BaseModel

from domain.dto.dtos import RegisterUserDTO


class UserCreateRequest(RegisterUserDTO):
    ...


class UserResponse(BaseModel):
    id: int

    class ConfigDict:
        from_attributes = True


class DeleteResponse(BaseModel):
    success: bool

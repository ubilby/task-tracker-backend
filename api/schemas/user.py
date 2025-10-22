from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    nickname: str

class UserResponse(BaseModel):
    id: int
    nickname: str

    class ConfigDict:
        from_attributes = True

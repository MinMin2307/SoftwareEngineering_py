from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    first_name: str
    last_name: str

class CreatePostDTO(BaseModel):
    text: str
    user_id: int

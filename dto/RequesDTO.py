from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    first_name: str
    last_name: str

class CreatePostDTO(BaseModel):
    image: str
    text: str
    user_id: int
from typing import List

from pydantic import BaseModel

class PostResponseDTO(BaseModel):
    id: int
    image: str
    text: str
    user_id: int

class UserResponseDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    posts: List[PostResponseDTO] = []







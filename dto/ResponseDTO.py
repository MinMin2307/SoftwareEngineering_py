from typing import List
from pydantic import BaseModel


class PostResponseDTO(BaseModel):
    id: int
    text: str
    user_id: int
    image_full_url: str
    image_thumb_url: str


class UserResponseDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    posts: List[PostResponseDTO] = []

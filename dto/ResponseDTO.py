from typing import List, Optional
from pydantic import BaseModel


class PostResponseDTO(BaseModel):
    id: int
    text: str
    user_id: int
    image_full_url: str
    image_thumb_url: str
    generated_text: Optional[str] = None
    generated_text_status: Optional[str] = None
    generated_text_error: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_status: Optional[str] = None
    sentiment_error: Optional[str] = None
    headline_text: Optional[str] = None
    headline_status: Optional[str] = None
    headline_error: Optional[str] = None


class UserResponseDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    posts: List[PostResponseDTO] = []

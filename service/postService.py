from database.database_sm import (
    save_post,
    get_postById,
    get_postImagesById,
    get_userById,
    get_postByUserId,
    search_postsByText,
    get_allPosts,
    get_userByName,
)
from dto.ResponseDTO import PostResponseDTO, UserResponseDTO
from service.queue import publish_resize_job

def _post_to_dto(post_id: int, text: str, user_id: int) -> PostResponseDTO:
    return PostResponseDTO(
        id=post_id,
        text=text,
        user_id=user_id,
        image_full_url=f"/post/{post_id}/image/full",
        image_thumb_url=f"/post/{post_id}/image/thumb",
    )

def createPost(image_bytes: bytes, image_mime: str, text: str, user_id: int) -> PostResponseDTO:
    post_id = save_post(
        image_full=image_bytes,
        image_full_mime=image_mime or "application/octet-stream",
        text=text,
        user_id=user_id,
    )
    publish_resize_job(post_id)
    return _post_to_dto(post_id, text, user_id)

def getPostById(id: int) -> PostResponseDTO:
    post = get_postById(id)
    return _post_to_dto(post_id=post[0], text=post[1], user_id=post[2])

def getAllPosts() -> list[PostResponseDTO]:
    rows = get_allPosts()
    return [_post_to_dto(row[0], row[1], row[2]) for row in rows]

def getPostByUserId(id: int) -> UserResponseDTO:
    user = get_userById(id)
    posts = get_postByUserId(id)
    postDTO = [_post_to_dto(post[0], post[1], post[2]) for post in posts]
    return UserResponseDTO(
        id=user[0],
        first_name=user[1],
        last_name=user[2],
        posts=postDTO,
    )

def searchPostByText(word: str) -> list[PostResponseDTO]:
    posts = search_postsByText(word)
    return [_post_to_dto(post[0], post[1], post[2]) for post in posts]

def getPostByUserName(first_name: str, last_name: str) -> UserResponseDTO:
    user = get_userByName(first_name, last_name)
    posts = get_postByUserId(user[0])
    postDTO = [_post_to_dto(post[0], post[1], post[2]) for post in posts]
    return UserResponseDTO(
        id=user[0],
        first_name=user[1],
        last_name=user[2],
        posts=postDTO,
    )

def getPostImagesById(id: int):
    return get_postImagesById(id)

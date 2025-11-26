from database.database_sm import save_post, get_postById, get_userById, get_postByUserId, search_postsByText
from dto.RequesDTO import CreatePostDTO
from dto.ResponseDTO import PostResponseDTO, UserResponseDTO
from model.post import Post


def createPost(data: CreatePostDTO):
    post = Post(data.image, data.text, data.user_id)
    save_post(post)
    return post


def getPostById(id: int) -> PostResponseDTO:
    post = get_postById(id)
    return PostResponseDTO(
        id=post[0],
        image=post[1],
        text=post[2],
        user_id=post[3]
    )

def getPostByUserId(id: int) -> UserResponseDTO:
    user = get_userById(id)
    posts = get_postByUserId(id)
    postDTO = [PostResponseDTO(
        id=post[0],
        image=post[1],
        text=post[2],
        user_id=post[3]
        )
        for post in posts
    ]
    return UserResponseDTO(
        id=user[0],
        first_name=user[1],
        last_name=user[2],
        posts= postDTO
    )

def searchPostByText(word: str) -> list[PostResponseDTO]:
    posts = search_postsByText(word)
    return [PostResponseDTO(
        id=posts[0],
        image=posts[1],
        text=posts[2],
        user_id=posts[3]
        )
        for post in posts
    ]




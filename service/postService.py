from database.database_sm import save_post, get_postById, get_userById, get_postByUserId, search_postsByText, get_allPosts
from dto.RequesDTO import CreatePostDTO
from dto.ResponseDTO import PostResponseDTO, UserResponseDTO


def createPost(data: CreatePostDTO) -> PostResponseDTO:
    post_id = save_post(data.image, data.text, data.user_id)

    return PostResponseDTO(
        id=post_id,
        image=data.image,
        text=data.text,
        user_id=data.user_id
    )



def getPostById(id: int) -> PostResponseDTO:
    post = get_postById(id)
    return PostResponseDTO(
        id=post[0],
        image=post[1],
        text=post[2],
        user_id=post[3]
    )
def getAllPosts() -> list[PostResponseDTO]:
    rows = get_allPosts()
    return [
        PostResponseDTO(
            id=row[0],
            image=row[1],
            text=row[2],
            user_id=row[3]
        )
        for row in rows
    ]

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
        id=post[0],
        image=post[1],
        text=post[2],
        user_id=post[3]
        )
        for post in posts
    ]




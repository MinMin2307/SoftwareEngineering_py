from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from dto.RequesDTO import CreateUserDTO
from dto.ResponseDTO import UserResponseDTO, PostResponseDTO

from service.postService import (
    createPost,
    getPostById,
    getPostByUserId,
    getAllPosts,
    searchPostByText,
    getPostByUserName,
    getPostImagesById,
)
from service.userService import createUser

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_index():
    return FileResponse("index.html")


@app.post("/user", response_model=UserResponseDTO)
def create_UserPoint(dto: CreateUserDTO):
    user = createUser(dto)
    return user


# NEU: multipart/form-data Upload (full-size wird gespeichert + thumbnail wird erzeugt)
@app.post("/post", response_model=PostResponseDTO)
async def create_PostPoint(
    file: UploadFile | None = File(None),
    text: str = Form(...),
    user_id: int = Form(...),
):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="No file content received.")

    # grobe Validierung (optional, aber hilfreich)
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    post = createPost(
        image_bytes=image_bytes,
        image_mime=file.content_type or "application/octet-stream",
        text=text,
        user_id=user_id,
    )
    return post


@app.get("/posts", response_model=list[PostResponseDTO])
def get_PostsPoint():
    posts = getAllPosts()
    return posts


@app.get("/post/{id}", response_model=PostResponseDTO)
def get_PostByIdPoint(id: int):
    post = getPostById(id)
    return post


@app.get("/post/{id}/image/full")
def get_PostImageFull(id: int):
    row = getPostImagesById(id)
    if row is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    image_full, image_full_mime, _, _ = row
    if image_full is None:
        raise HTTPException(status_code=404, detail="Full image not stored.")
    return Response(content=bytes(image_full), media_type=image_full_mime or "application/octet-stream")


@app.get("/post/{id}/image/thumb")
def get_PostImageThumb(id: int):
    row = getPostImagesById(id)
    if row is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    _, _, image_thumb, image_thumb_mime = row
    if image_thumb is None:
        raise HTTPException(status_code=404, detail="Thumbnail not stored.")
    return Response(content=bytes(image_thumb), media_type=image_thumb_mime or "application/octet-stream")


@app.get("/user/by-name", response_model=UserResponseDTO)
def get_UserByNamePoint(first_name: str, last_name: str):
    user = getPostByUserName(first_name, last_name)
    return user


@app.get("/user/{id:int}", response_model=UserResponseDTO)
def get_UserByIdPoint(id: int):
    user = getPostByUserId(id)
    return user


@app.get("/posts/search", response_model=list[PostResponseDTO])
def get_PostByTextPoint(text: str):
    post = searchPostByText(text)
    return post

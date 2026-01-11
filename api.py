from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from service.queue import publish_textgen_job, publish_sentiment_job, publish_headline_job
from database.database_sm import get_postById
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
    return createUser(dto)

from typing import Optional
from fastapi import UploadFile, File, Form, HTTPException

@app.post("/post", response_model=PostResponseDTO)
async def create_PostPoint(
    file: Optional[UploadFile] = File(None),   # <- optional
    text: str = Form(...),
    user_id: int = Form(...),
):
    image_bytes = None
    image_mime = None

    if file is not None:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="No file content received.")
        if not (file.content_type or "").startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file is not an image.")
        image_mime = file.content_type or "application/octet-stream"

    return createPost(
        image_bytes=image_bytes,
        image_mime=image_mime,
        text=text,
        user_id=user_id,
    )


@app.get("/posts", response_model=list[PostResponseDTO])
def get_PostsPoint():
    return getAllPosts()

@app.get("/post/{id}", response_model=PostResponseDTO)
def get_PostByIdPoint(id: int):
    return getPostById(id)

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
        raise HTTPException(status_code=404, detail="Thumbnail not ready yet.")
    return Response(content=bytes(image_thumb), media_type=image_thumb_mime or "application/octet-stream")

@app.get("/user/by-name", response_model=UserResponseDTO)
def get_UserByNamePoint(first_name: str, last_name: str):
    return getPostByUserName(first_name, last_name)

@app.get("/user/{id}", response_model=UserResponseDTO)
def get_UserByIdPoint(id: int):
    return getPostByUserId(id)

@app.get("/posts/search", response_model=list[PostResponseDTO])
def get_PostByTextPoint(text: str):
    return searchPostByText(text)

@app.post("/post/{id}/textgen")
def trigger_textgen(id: int):
    post = get_postById(id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    publish_textgen_job(id)
    return {"status": "queued", "post_id": id}

@app.post("/post/{id}/sentiment")
def trigger_sentiment(id: int):
    post = get_postById(id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    publish_sentiment_job(id)
    return {"status": "queued", "post_id": id}

@app.post("/post/{id}/headline")
def trigger_headline(id: int):
    post = get_postById(id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    publish_headline_job(id)
    return {"status": "queued", "post_id": id}

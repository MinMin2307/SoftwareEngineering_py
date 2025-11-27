from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dto.RequesDTO import CreateUserDTO, CreatePostDTO
from dto.ResponseDTO import UserResponseDTO, PostResponseDTO
from service.postService import (
    createPost,
    getPostById,
    getPostByUserId,
    getAllPosts,
    searchPostByText,
    getPostByUserName,
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


@app.post("/user", response_model=UserResponseDTO)
def create_UserPoint(dto: CreateUserDTO):
    user = createUser(dto)
    return user


@app.post("/post", response_model=PostResponseDTO)
def create_PostPoint(dto: CreatePostDTO):
    post = createPost(dto)
    return post


@app.get("/posts", response_model=list[PostResponseDTO])
def get_PostsPoint():
    posts = getAllPosts()
    return posts


@app.get("/post/{id}", response_model=PostResponseDTO)
def get_PostByIdPoint(id: int):
    post = getPostById(id)
    return post


@app.get("/user/{id}", response_model=UserResponseDTO)
def get_UserByIdPoint(id: int):
    user = getPostByUserId(id)
    return user


@app.get("/user/by-name", response_model=UserResponseDTO)
def get_UserByNamePoint(first_name: str, last_name: str):
    user = getPostByUserName(first_name, last_name)
    return user


@app.get("/posts/search", response_model=list[PostResponseDTO])
def get_PostByTextPoint(text: str):
    post = searchPostByText(text)
    return post





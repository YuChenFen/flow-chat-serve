from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import io
import os
import random

IMAGE_BASE_PATH = "./static/image"
random_file_list = os.listdir(f"{IMAGE_BASE_PATH}/random")

file_api_router = APIRouter()

@file_api_router.get("/image/random")
async def random_image():
    try:
        random_num = random.randint(0, len(random_file_list)-1)
        file_name = random_file_list[random_num]
        def iterfile(file_name):
            with open(f"{IMAGE_BASE_PATH}/random/{file_name}", "rb") as image_file:
                yield from image_file
        return StreamingResponse(iterfile(file_name), media_type="image/webp")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@file_api_router.get("/image/community/{image_name}")
async def community_image(image_name: str):
    try:
        return FileResponse(f"{IMAGE_BASE_PATH}/community/{image_name}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@file_api_router.get("/image/userAvatar/{image_name}")
async def user_image(image_name: str):
    try:
        return FileResponse(f"{IMAGE_BASE_PATH}/userAvatar/{image_name}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

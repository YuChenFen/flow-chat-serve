# import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import file_api
# 数据库
from api.db.index import db_api_router
from api.db import community
from api.db import user
from api.db import message
# 中间件
from middleware import JWTMiddleware


PORT_API = 8008

app = FastAPI(
    title="API server",
    version="1.0.0",
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
        Middleware(JWTMiddleware)
    ],
)

app.include_router(file_api.file_api_router, prefix="/v1/file", tags=["file"])
app.include_router(db_api_router, prefix="/v1/db", tags=["db"])

# Configure CORS settings
# origins = [
#     "http://localhost:3000",
#     "*"
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )




def start_api_server():
    try:
        print("Starting API server...")
        uvicorn.run(app, host="0.0.0.0", port=PORT_API, log_level="info")
        return True
    except:
        print("Failed to start API server")
        return False


if __name__ == "__main__":
    start_api_server()
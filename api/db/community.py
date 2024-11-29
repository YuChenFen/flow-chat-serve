from fastapi import File, UploadFile, Form
from api.db.index import db_api_router
import sqlite3
from utils import time_utils
from starlette.requests import Request

con = sqlite3.connect("./database.db")
cur = con.cursor()

@db_api_router.get("/community/data")
async def get_data():
    """
        获取所有社区数据
    """
    try:
        data = cur.execute("SELECT * FROM community")
        return {
            "code": 200,
            "data": data.fetchall(),
            "success": True,
            "message": "Success"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

@db_api_router.post("/community/data")
async def post_data(
    request: Request,
    description: str = Form(title='简介说明'), 
    content:object = Form(title='内容'), 
    image: UploadFile = File(...)
):
    """
        添加上传社区数据
    """
    try:
        user_id = request.state.user_id
        now = time_utils.get_now()
        image_name = str(user_id) + "_" + str(time_utils.get_timestamp(now)) + image.filename
        with open(f"./static/image/community/{image_name}", "wb") as buffer:
            buffer.write(image.file.read())
        cur.execute("INSERT INTO community (userId, updateTime, description, content, image) VALUES (?, ?, ?, ?, ?)",(user_id, now, description, content, f'http://127.0.0.1:8008/v1/file/image/community/{image_name}'))
        con.commit()
        return {
            "code": 200,
            "data": None,
            "success": True,
            "message": "Success"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }
    
@db_api_router.get("/community/query")
async def query(search: str, where: str = None):
    """
    获取指定社区数据

    - search 查询数据，包含 [id, userId, userName, update_time, description, content, image]，例如查询名字和时间`name, update_time`
    - where 条件，例如 `id=1`
    """
    try:
        # 有注入风险 - 可在前面进行正则校验，如有异常就抛出
        where = f" WHERE {where}" if where else ""
        data = cur.execute(f"SELECT {search} FROM community {where}",)
        return {
            "code": 200,
            "data": data.fetchall(),
            "success": True,
            "message": "获取社区数据成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }
    
@db_api_router.get("/community/list")
async def get_list(userName: str = None, description = None, page: int = 1, size: int = 10):
    """
    获取社区列表
    """
    try:
        where = ""
        if userName or description:
            where += "WHERE "
            where += "userName LIKE '%" + userName + "%'" if userName else ""
            if userName and description:
                where += " OR "
            where += "description LIKE '%" + description + "%'" if description else ""
        data = cur.execute(f"SELECT community.id, user.userName, community.description, community.image, community.updateTime, user.userAvatar FROM community INNER JOIN user ON community.userId = user.id {where} LIMIT ?, ?", ((page-1)*size, size))
        return {
            "code": 200,
            "data": data.fetchall(),
            "success": True,
            "message": "获取社区列表成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

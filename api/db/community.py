from fastapi import File, UploadFile, Form
from api.db.index import db_api_router
import sqlite3
from utils import time_utils
from starlette.requests import Request
from pydantic import BaseModel
import os

con = sqlite3.connect("./database.db")
cur = con.cursor()

@db_api_router.get("/community/data", summary="获取所有社区数据")
async def get_data():
    """
        获取所有社区数据

        返回值：
        - code 状态码
        - data 数据
        - success 是否成功
        - message 提示信息

        data: 
        - id 社区id
        - userId 用户id
        - updateTime 更新时间
        - description 简介
        - content 内容
        - image 图片
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

@db_api_router.post("/community/data", summary="上传社区数据")
async def post_data(
    request: Request,
    description: str = Form(title='简介说明'), 
    content:object = Form(title='内容'), 
    image: UploadFile = File(...)
):
    """
        添加上传社区数据

        - description 简介说明
        - content 内容
        - image 图片文件

        返回值：
        - code 状态码
        - data 数据
        - success 是否成功
        - message 提示信息
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
    
@db_api_router.get("/community/query", summary="查询社区数据")
async def query(search: str, where: str = None):
    """
    获取指定社区数据

    - search 查询数据，包含 [id, userId, userName, update_time, description, content, image]，例如查询名字和时间`name, update_time`
    - where 条件，例如 `id=1`

    返回值：
    - code 状态码
    - data 数据
    - success 是否成功
    - message 提示信息

    data: 
    - 根据search返回对应值
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
    
@db_api_router.get("/community/list", summary="获取社区列表")
async def get_list(userName: str = None, description = None, page: int = 1, size: int = 10):
    """
    获取社区列表

    - userName 用户名
    - description 简介
    - page 页码
    - size 每页数量

    返回值：
    - code 状态码
    - data 数据
    - success 是否成功
    - message 提示信息

    data:
    - totle 总数
    - id 社区id
    - userName 用户名
    - description 简介
    - image 图片
    - updateTime 更新时间
    - userAvatar 用户头像

    """
    try:
        where = ""
        if userName or description:
            where += "WHERE "
            where += "userName LIKE '%" + userName + "%'" if userName else ""
            if userName and description:
                where += " OR "
            where += "description LIKE '%" + description + "%'" if description else ""
        totle = cur.execute(f"SELECT COUNT(*) FROM community JOIN user ON community.userId = user.id {where}").fetchone()[0]
        data = cur.execute(f"SELECT community.id, user.userName, community.description, community.image, community.updateTime, user.userAvatar FROM community INNER JOIN user ON community.userId = user.id {where} LIMIT ?, ?", ((page-1)*size, size))
        return {
            "code": 200,
            "data": {
                "totle": totle,
                "data": [{
                    "id": item[0],
                    "userName": item[1],
                    "description": item[2],
                    "image": item[3],
                    "updateTime": item[4],
                    "userAvatar": item[5]
                } for item in data.fetchall()]
            },
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

@db_api_router.delete("/community/data", summary="删除社区数据")
async def delete_community(request: Request, id: str):
    """
    删除社区数据
    - id 社区id

    返回值：
    - code 状态码
    - data 数据
    - success 是否成功
    - message 提示信息
    """
    try:
        user_id = request.state.user_id
        community_user_id = cur.execute("SELECT userId FROM community WHERE id=?",(id,)).fetchall()[0][0]
        userRole = cur.execute(f"SELECT userRole FROM user WHERE id=?", (
            user_id, 
        )).fetchall()[0][0]
        if user_id != community_user_id and userRole not in ['superAdmin', 'admin']:
            return {
                "code": 500,
                "data": None,
                "success": False,
                "message": "不是自己的评论，无法删除"
            }
        image_name = cur.execute("SELECT image FROM community WHERE id=?",(id,)).fetchone()[0].split('/')[-1]
        cur.execute("DELETE FROM community WHERE id=?",(id,))
        cur.execute("DELETE FROM community_comment WHERE communityId=?",(id,))
        con.commit()
        os.remove(f"./static/image/community/{image_name}")
        return {
            "code": 200,
            "data": None,
            "success": True,
            "message": "删除社区数据成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }


class Comment(BaseModel):
    communityId: str
    content: str
@db_api_router.post("/community/comment", summary="提交社区评论")
async def post_comment(request: Request, comment: Comment):
    """
    添加评论

    - communityId 社区id
    - content 评论内容

    返回值：
    - code 状态码
    - data 数据
    - success 是否成功
    - message 提示信息
    """
    try:
        user_id = request.state.user_id
        cur.execute("INSERT INTO community_comment (communityId, userId, content) VALUES (?, ?, ?)",(comment.communityId, user_id, comment.content))
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
    
@db_api_router.get("/community/comment/list", summary="获取社区评论列表")
async def get_comment_list(communityId: str, page: int = 1, size: int = 10):
    """
    获取评论列表

    - communityId 社区id
    - page 页码
    - size 每页数量

    返回值：
    - code 状态码
    - data 数据
    - success 是否成功
    - message 提示信息

    data:
    - id 评论id
    - userName 用户名
    - content 评论内容
    - createTime 创建时间
    - userAvatar 用户头像
    """
    try:
        data = cur.execute(f"SELECT community_comment.id, user.userName, community_comment.content, community_comment.createTime, user.userAvatar FROM community_comment INNER JOIN user ON community_comment.userId = user.id WHERE communityId = ? LIMIT ?, ?", (communityId, (page-1)*size, size))
        return {
            "code": 200,
            "data": [{"id": i[0], "userName": i[1], "content": i[2], "createTime": i[3], "userAvatar": i[4]} for i in data.fetchall()],
            "success": True,
            "message": "获取评论列表成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

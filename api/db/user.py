from pydantic import BaseModel
from fastapi import Form, File, UploadFile
from starlette.requests import Request
from api.db.index import db_api_router
import sqlite3
import hashlib
from utils import jwt_utils
import os

con = sqlite3.connect("./database.db")
cur = con.cursor()

@db_api_router.get("/login")
async def login(userAccount: str, userPassword: str):
    try:
        # 查询是否有该用户
        userPassword = hashlib.md5(userPassword.encode()).hexdigest()
        result = cur.execute(f"SELECT id, userRole, isDelete FROM user WHERE userAccount=? AND userPassword=?", (
            userAccount, userPassword
        )).fetchall()
        if result:
            if result[0][2] == 1:
                return {
                    "code": 400,
                    "data": None,
                    "success": False,
                    "message": "该用户已被禁用"
                }
            token = jwt_utils.generate_jwt_token(result[0][0])
            return {
                "code": 200,
                "data": {
                    "token":  token,
                    "userRole": result[0][1]
                },
                "success": True,
                "message": "登录成功"
            }
        else:
            return {
                "code": 400,
                "data": None,
                "success": False,
                "message": "用户名或密码错误"
            }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

class User(BaseModel):
    userAccount: str
    userPassword: str

@db_api_router.post("/register")
async def register(user: User):
    try:
        userAccount = user.userAccount
        userPassword = user.userPassword
        # 查询是否有该用户
        userPassword = hashlib.md5(userPassword.encode()).hexdigest()
        result = cur.execute(f"SELECT id FROM user WHERE userAccount=?", (
            userAccount, 
        )).fetchall()
        if result:
            return {
                "code": 400,
                "data": None,
                "success": False,
                "message": "用户已存在"
            }
        else:
            userAvatar = "http://127.0.0.1:8008/v1/file/image/userAvatar/empty-user.png"
            cur.execute(f"INSERT INTO user (userAccount, userPassword, userAvatar) VALUES (?, ?, ?)", (
                userAccount, userPassword, userAvatar
            ))
            con.commit()
            return {
                "code": 200,
                "data": None,
                "success": True,
                "message": "注册成功"
            }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }
    
@db_api_router.get("/user/info")
async def get_user_info(request: Request):
    try:
        user_id = request.state.user_id
        result = cur.execute(f"SELECT userAvatar, userName, gender, phone, email, userRole FROM user WHERE id=?", (
            user_id, 
        )).fetchall()
        if result:
            return {
                "code": 200,
                "data": {
                    "userAvatar": result[0][0],
                    "userName": result[0][1],
                    "gender": result[0][2],
                    "phone": result[0][3],
                    "email": result[0][4],
                    "userRole": result[0][5]
                },
                "success": True,
                "message": "获取用户信息成功"
            }
        return {
            "code": 400,
            "data": None,
            "success": False,
            "message": "用户不存在"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

@db_api_router.post("/user/update")
async def update(
    request: Request,
    userAvatar: UploadFile = File(default=None), 
    userName: str = Form(title='用户名', default=''), 
    gender:str = Form(title='性别', default=''), 
    phone: str = Form(title='手机号', default=''),
    email: str = Form(title='邮箱', default='')
    ):
    try:
        user_id = request.state.user_id
        update_list = []
        if userAvatar is not None:
            image_name = f"{user_id}{userAvatar.filename}"
            path = f"./static/image/userAvatar/{image_name}"
            with open(path, "wb") as f:
                f.write(userAvatar.file.read())
            # 查找并删除用户原头像
            result = cur.execute(f"SELECT userAvatar FROM user WHERE id=?", (
                user_id, 
            )).fetchall()
            if result[0][0] != "http://127.0.0.1:8008/v1/file/image/userAvatar/empty-user.png":
                os.remove(result[0][0].replace("http://127.0.0.1:8008/v1/file", "./static"))
            update_list.append({
                "key": "userAvatar",
                "value": f"http://127.0.0.1:8008/v1/file/image/userAvatar/{image_name}"
            })
        if userName != '':
            update_list.append({
                "key": "userName",
                "value": userName
            })
        if gender != '':
            update_list.append({
                "key": "gender",
                "value": gender
            })
        if phone != '':
            update_list.append({
                "key": "phone",
                "value": phone
            })
        if email != '':
            update_list.append({
                "key": "email",
                "value": email
            })

        sql = "UPDATE user SET "
        for i, item in enumerate(update_list):
            sql += f"{item['key']}='{item['value']}',"
        sql += f"updateTime=datetime('now','localtime')"
        sql += f" WHERE id={user_id}"
        cur.execute(sql)
        con.commit()
        return {
            "code": 200,
            "data": None,
            "success": True,
            "message": "更新成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }
    
@db_api_router.get("/user/query")
async def query(search: str, where: str = None, page: int = 1, size: int = 10):
    """
    获取指定用户数据

    - search 查询数据，包含 [id, userAccount, userName, gender, phone, email, userAvatar, updateTime]，例如查询名字和时间`userName, updateTime`
    - where 条件，例如 `id=1`
    """
    try:
        where = f" WHERE {where}" if where else ""
        totle = cur.execute(f"SELECT COUNT(*) FROM user {where}").fetchall()
        sql = f"SELECT {search} FROM user {where} LIMIT {(page-1)*size},{size}"
        data = cur.execute(sql)
        return {
            "code": 200,
            "data": {
                "data": data.fetchall(),
                "totle": totle[0][0]
            },
            "success": True,
            "message": "获取用户信息成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

class Information(BaseModel):
    userAccount: str
    userRole: str
    isDelete: int
    
@db_api_router.post("/user/change")
async def change(request: Request, information: Information):
    try:
        user_id = request.state.user_id
        # 查询是不是管理员
        result = cur.execute(f"SELECT userRole FROM user WHERE id=?", (
            user_id, 
        )).fetchall()
        if result[0][0] != "superAdmin" or result[0][0] == 'admin':
            return {
                "code": 400,
                "data": None,
                "success": False,
                "message": "权限不足"
            }
        else:
            cur.execute(f"UPDATE user SET userRole=?, isDelete=? WHERE userAccount=?", (
                information.userRole, 
                information.isDelete, 
                information.userAccount
            ))
            con.commit()
            return {
                "code": 200,
                "data": None,
                "success": True,
                "message": "更新成功"
            }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }
    

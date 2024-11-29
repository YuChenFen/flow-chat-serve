import time
import jwt

JWT_TOKEN_EXPIRE_TIME = 60 * 60 * 2     # 2 小时有效时间
JWT_SECRET_KEY = "secret"               # 密钥
JWT_ALGORITHM = "HS256"                 # 加密算法

def generate_jwt_token(user_id: str):
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + JWT_TOKEN_EXPIRE_TIME
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {
            "code": 200,
            "success": True,
            "message": "Token验证通过",
            "user_id": payload["user_id"]
        }
    except jwt.ExpiredSignatureError:
        return {
            "code": 401,
            "success": False,
            "message": "Token已过期"
        }
    except jwt.InvalidTokenError:
        return {
            "code": 401,
            "success": False,
            "message": "无效的Token"
        }
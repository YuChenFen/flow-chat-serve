from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
# jwt
from utils import jwt_utils

class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.exempt_paths = ["/v1/db/login", "/v1/db/register", "/v1/file"]

    def is_exempt(self, path:str)->bool:
        # return True
        return not path.startswith("/v1") or path.startswith(tuple(self.exempt_paths))

    async def dispatch(self, request: Request, call_next):
        # return await call_next(request)
        path = request.url.path
        if self.is_exempt(path):
            return await call_next(request)
        
        token = request.headers.get("Authorization")
        if token:
            message = jwt_utils.verify_jwt_token(token=token[7:])
            if message["success"]:
                request.state.user_id = message["user_id"]
                response = await call_next(request)
                return response
            else:
                return JSONResponse({
                "code": 401,
                "data": None,
                "success": False,
                "message": message["message"]
            })
        else:
            return JSONResponse({
                "code": 401,
                "data": None,
                "success": False,
                "message": "请求未携带token"
            })

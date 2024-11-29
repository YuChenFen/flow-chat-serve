from pydantic import BaseModel
from starlette.responses import StreamingResponse
from starlette.requests import Request
from api.db.index import db_api_router
import sqlite3
import asyncio
import json

con = sqlite3.connect("./database.db")
cur = con.cursor()

class Message(BaseModel):
    toUserId: int
    content: str
    type: str

link_map = {}

async def event_generator(user_id: int, client: asyncio.Queue):
    try:
        while True:
            data = await client.get()
            yield json.dumps(data)
    except asyncio.CancelledError as e:
        del link_map[user_id]
        raise e

@db_api_router.get("/message/link")
async def link(request: Request):
    try:
        user_id = request.state.user_id
        link_map[user_id] = asyncio.Queue()
        return StreamingResponse(event_generator(user_id, link_map[user_id]), media_type="text/event-stream")
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

@db_api_router.post("/message/send")
async def send(request: Request, message: Message):
    try:
        from_user_id = request.state.user_id
        to_user_id = message.toUserId
        unread = 1
        if to_user_id in link_map:
            unread = 0
            await link_map[to_user_id].put({
                "fromUserId": from_user_id,
                "type": message.type,
                "content": message.content
            })
        cur.execute("INSERT INTO message (fromId, toId, content, type, unread) VALUES (?, ?, ?, ?, ?)", (from_user_id, to_user_id, message.content, message.type, unread))
        con.commit()
        return {
            "code": 200,
            "data": None,
            "success": True,
            "message": "发送成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

@db_api_router.get("/message/unread")
async def unread(request: Request):
    try:
        user_id = request.state.user_id
        result = cur.execute(f"SELECT fromId, content, type, createTime FROM message WHERE toId=? AND unread=1", (user_id,)).fetchall()
        cur.execute(f"UPDATE message SET unread=0 WHERE toId=?", (user_id,))
        con.commit()
        print(result)
        return {
            "code": 200,
            "data": [
                {
                    "fromUserId": row[0],
                    "content": row[1],
                    "type": row[2],
                    "createTime": row[3]
                } for row in result
            ],
            "success": True,
            "message": "查询成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

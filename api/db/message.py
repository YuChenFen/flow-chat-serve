from pydantic import BaseModel
from starlette.responses import StreamingResponse
from starlette.requests import Request
from api.db.index import db_api_router
from utils import random_utils
from urllib.parse import quote
from vectorDatabase.index import vd_query
import sqlite3
import asyncio
import json


con = sqlite3.connect("./database.db")
cur = con.cursor()

class Message(BaseModel):
    to: str
    content: str
    type: str

link_map = {}
# 实时协作
room_ollaboration = {}

async def event_generator(user_id: int, client: asyncio.Queue):
    try:
        while True:
            data = await client.get()
            json_data = json.dumps(data)
            yield quote(json_data) + '[END_FLAG]'
    except asyncio.CancelledError as e:
        del link_map[user_id]
        for room_id in room_ollaboration.keys():
            if user_id in room_ollaboration[room_id]:
                room_ollaboration[room_id].remove(user_id)
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

@db_api_router.get("/message/collaboration/create")
async def create_collaboration_room(request: Request):
    try:
        user_id = request.state.user_id
        room_id = random_utils.get_room_id()
        room_ollaboration[room_id] = [link_map[user_id]]
        return {
            "code": 200,
            "data": room_id,
            "success": True,
            "message": "创建成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

@db_api_router.get("/message/collaboration/join")
async def join_collaboration_room(request: Request, roomId: str):
    try:
        user_id = request.state.user_id
        if roomId not in room_ollaboration:
            return {
                "code": 400,
                "data": None,
                "success": False,
                "message": "房间不存在"
            }
        room_ollaboration[roomId].append(link_map[user_id])
        return {
            "code": 200,
            "data": None,
            "success": True,
            "message": "加入成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "success": False,
            "message": f"Error: {e}"
        }

@db_api_router.get("/message/collaboration/leave")
async def leave_collaboration_room(request: Request, roomId: str):
    try:
        user_id = request.state.user_id
        if roomId not in room_ollaboration:
            return {
                "code": 400,
                "data": None,
                "success": False,
                "message": "房间不存在"
            }
        room_ollaboration[roomId].remove(link_map[user_id])
        if len(room_ollaboration[roomId]) == 0:
            del room_ollaboration[roomId]
        return {
            "code": 200,
            "data": None,
            "success": True,
            "message": "离开成功"
        }
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
        if message.type == 'text':
            from_user_id = request.state.user_id
            to_user_id = int(message.to)
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
        elif message.type == 'chartRoom':
            from_user_id = request.state.user_id
            room_id = message.to
            for client in room_ollaboration[room_id]:
                if client != link_map[from_user_id]:
                    await client.put({
                        "fromUserId": from_user_id,
                        "type": message.type,
                        "content": message.content
                    })
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

class vbData(BaseModel):
    text: str
    query: str

@db_api_router.post("/message/vd/query")
async def vd_query_gat(vb_data: vbData):
    '''
        查询相关的数据
        text: 所有内容 
        - 格式为 
        ```
        |节点|节点内容|
        |节点一|节点一内容|
        |...|...|
        
        | 源节点 | 目标节点 | 关系名称 | 关系内容 |
        | ... | ... | ... | ... |
        ```

        query: 查询语句

        返回： 最多一百条结果
        nodes_results: 节点查询结果
        edges_results: 边查询结果
    '''
    try:
        data = vb_data.text.split("\n\n")
        nodes = data[0].split("\n")[1:]
        edges = data[1].split("\n")[1:]
        nodes_results = vd_query(nodes, vb_data.query, 250)
        edges_results = vd_query(edges, vb_data.query, 250)
        return {
            "code": 200,
            "data": {
                "nodes_results": nodes_results, 
                "edges_results": edges_results
            },
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


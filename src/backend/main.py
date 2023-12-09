from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi_users import fastapi_users, FastAPIUsers
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth.auth import auth_backend
from auth.schemas import UserRead, UserCreate
from auth.database import User
from auth.manager import get_user_manager

import sys,os
sys.path.insert(0, os.getcwd() + '/src/backend/logic')
from logic.websocket_logic import ConnectionManager, NoConnection

import uvicorn

import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

app = FastAPI(
    title="Semantle Ru",
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/database",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.mount("/static", StaticFiles(directory="res/web_content/static"), name="static")

templates = Jinja2Templates(directory="res/web_content/templates")

manager = ConnectionManager()

#TODO унести это отсюда куда-нибудь типа "routes.py"
@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#TODO подключение оставить тут, получение сообщений отправить 
import json
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    id = await manager.connect(websocket)
    game_session = manager.active_connections[id].game_session
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            if not "type" in data_json:
                continue
            
            if data_json["type"] == "word":
                similarity = game_session.handleWord(data_json["word"])
                game_state = game_session.state
                answer = {"type" : "word", 
                          "word" : data_json["word"], 
                          "similarity" : similarity,
                          "game_state" : game_state.name}
                await manager.send_personal_message(json.dumps(answer), id)
                continue
            if data_json["type"] == "init":
                game_session.resetGame()
                try: 
                    game_session.initWord()
                except NoConnection:
                    answer = {"type" : "init",
                        "result" : "true"}
                    await manager.send_personal_message(json.dumps(answer), id)
                    continue
                answer = {"type" : "init",
                          "result" : "false"}
                await manager.send_personal_message(json.dumps(answer), id)
                continue
            if data_json["type"] == "hint":
                hint = game_session.getHint()
                if hint:
                    answer = {"type" : "hint",
                              "word" : hint[0],
                              "similarity" : hint[1]}
                else:
                    answer = {"type" : "hint"}
                await manager.send_personal_message(json.dumps(answer), id)
                continue                
            else:
                answer = {"type" : "error",
                          "text" : "Неизвестный тип сообщения"}
                await manager.send_personal_message(json.dumps(answer), id)
                continue                
    except WebSocketDisconnect:
        manager.disconnect(id)

#Это тут для возможности дебага
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
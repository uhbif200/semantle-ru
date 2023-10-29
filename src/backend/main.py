from fastapi import FastAPI
from fastapi_users import fastapi_users, FastAPIUsers

from auth.auth import auth_backend
from auth.schemas import UserRead, UserCreate
from auth.database import User
from auth.manager import get_user_manager

from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(
    title="Semantle Ru",
)


app.mount("/static", StaticFiles(directory="res/web_content"), name="static")

#TODO унести это отсюда
@app.get('/')
async def home(request: Request):
    return FileResponse('res/web_content/index.html')

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

#Это тут для возможности дебага
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
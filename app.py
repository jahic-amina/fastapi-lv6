from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import create_db_and_tables
from auth.config import fastapi_users, auth_backend
from auth.users import UserCreate, UserRead, UserUpdate
from routers.studenti import router as studenti_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # async!
    yield


app = FastAPI(
    title="Studentski registar",
    description="REST API za upravljanje studentima sa JWT autentifikacijom",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.include_router(studenti_router)


@app.get("/", tags=["root"])
def root():
    return {"poruka": "Studentski registar API radi!", "dokumentacija": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
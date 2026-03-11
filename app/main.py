from fastapi import FastAPI
from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router
from app.api.routes.auth import router as auth_router

app = FastAPI()

app.include_router(users_router)
app.include_router(projects_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "FastAPI + PostgreSQL connection success"}
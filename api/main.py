from fastapi import FastAPI, APIRouter
from api.v1.routers import auth, users, jobs, applications, companies, admin
from api.db import ping_db


API_PREFIX = "/api/v1"


def create_app():
    app = FastAPI(title="JobRadar API", version="1.0.0")
    
    v1_router = APIRouter(prefix=API_PREFIX)
    v1_router.include_router(auth.router,         tags=["auth"])
    v1_router.include_router(users.router,        tags=["users"])
    v1_router.include_router(jobs.router,         tags=["jobs"])
    v1_router.include_router(applications.router, prefix="/applications", tags=["applications"])
    v1_router.include_router(companies.router,    tags=["companies"])
    v1_router.include_router(admin.router,        tags=["admin"])

    app.include_router(v1_router)
    return app

app = create_app()


@app.get("/healthz")
async def healthz():
    await ping_db()
    return {"ok": True}

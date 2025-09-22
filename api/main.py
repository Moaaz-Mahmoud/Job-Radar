from fastapi import FastAPI, APIRouter
from api.v1.routers import auth, users, jobs, applications, companies, admin


API_PREFIX = "/api/v1"


def create_app():
    app = FastAPI(title="JobRadar API", version="1.0.0")
    
    v1_router = APIRouter()
    v1_router.include_router(auth.router,         prefix="/auth",         tags=["auth"])
    v1_router.include_router(users.router,        prefix="/users",        tags=["users"])
    v1_router.include_router(jobs.router,         prefix="/jobs",         tags=["jobs"])
    v1_router.include_router(applications.router, prefix="/applications", tags=["applications"])
    v1_router.include_router(companies.router,    prefix="/companies",    tags=["companies"])
    v1_router.include_router(admin.router,        prefix="/admin",        tags=["admin"])

    app.include_router(v1_router, prefix=API_PREFIX)
    return app

app = create_app()

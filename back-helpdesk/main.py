from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.tickets_public import router as tickets_public_router
from app.routers.tickets_mda import router as tickets_mda_router
from app.routers.dashboard import router as dashboard_router
from app.routers.admin import router as admin_router

app = FastAPI(title="Mesa de Ayuda API - SP Driven")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción restringe
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tickets_public_router)
app.include_router(tickets_mda_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
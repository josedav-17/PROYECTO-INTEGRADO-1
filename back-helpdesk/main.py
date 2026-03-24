from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.tickets import router as tickets_router

app = FastAPI(title="Mesa de Ayuda API - SP Driven")

origins = [
    "https://front-helpdesk.vercel.app",
    "http://localhost:4200",
    "https://front-helpdesk-two.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tickets_router)
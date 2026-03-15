from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import require_roles
from app.schemas.auth import LoginIn, LoginOut
from app.schemas.users import UserCreateIn, UserUpdateIn

from app.services.auth_service import AuthService
from app.services.users_service import UsersService

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

def get_users_service(db: Session = Depends(get_db)):
    return UsersService(db)


# ---------------- LOGIN ----------------
@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn, svc: AuthService = Depends(get_auth_service)):
    return svc.login(payload.email, payload.password)


# ---------------- USERS ----------------
@router.post("/users", dependencies=[Depends(require_roles("ADMIN"))])
def create_user(
    payload: UserCreateIn,
    svc: UsersService = Depends(get_users_service),
):
    return svc.create_user(payload)


@router.get("/users", dependencies=[Depends(require_roles("ADMIN"))])
def list_users(
    svc: UsersService = Depends(get_users_service),
):
    return svc.list_users()


@router.patch("/users/{user_id}", dependencies=[Depends(require_roles("ADMIN"))])
def update_user(
    user_id: str,
    payload: UserUpdateIn,
    svc: UsersService = Depends(get_users_service),
):
    return svc.update_user(user_id, payload)


@router.delete("/users/{user_id}", dependencies=[Depends(require_roles("ADMIN"))])
def delete_user(
    user_id: str,
    svc: UsersService = Depends(get_users_service),
):
    return svc.delete_user(user_id)
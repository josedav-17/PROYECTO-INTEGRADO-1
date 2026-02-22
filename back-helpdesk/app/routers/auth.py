from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.auth import LoginIn, LoginOut
from app.core.security import verify_password, create_access_token
from app.core.config import JWT_SECRET, JWT_ALG, ACCESS_TOKEN_EXPIRE

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    q = text("SELECT * FROM fn_auth_get_user_by_email(:em)")
    row = db.execute(q, {"em": str(payload.email)}).mappings().first()

    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(
        payload={
            "sub": row["id"],
            "email": row["email"],
            "rol": row["rol"],
            "area": row.get("area"),
            "nombre": row["nombre"],
        },
        secret=JWT_SECRET,
        alg=JWT_ALG,
        expires_delta=ACCESS_TOKEN_EXPIRE,
    )

    return {
        "access_token": token,
        "user": {
            "id": row["id"],
            "email": row["email"],
            "rol": row["rol"],
            "area": row.get("area"),
            "nombre": row["nombre"],
        },
    }
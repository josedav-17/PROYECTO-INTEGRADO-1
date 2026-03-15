from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException

from app.core.security import verify_password, create_access_token
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, email: str, password: str):
        row = (
            self.db.execute(
                text("SELECT * FROM fn_auth_get_user_by_email(:em)"),
                {"em": email},
            )
            .mappings()
            .first()
        )

        if not row:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if "is_active" in row and row["is_active"] is False:
            raise HTTPException(status_code=403, detail="Usuario desactivado")

        if not verify_password(password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        token = create_access_token(
            payload={
                "sub": row["id"],
                "email": row["email"],
                "rol": row["rol"],
                "area": row.get("area"),
                "nombre": row["nombre"],
            },
            secret=SECRET_KEY,
            alg=ALGORITHM,
            expires_delta=ACCESS_TOKEN_EXPIRE,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": row["id"],
                "email": row["email"],
                "rol": row["rol"],
                "area": row.get("area"),
                "nombre": row["nombre"],
            },
        }
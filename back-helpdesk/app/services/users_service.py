from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from uuid import uuid4

from app.core.security import hash_password


class UsersService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, payload):
        exists = self.db.execute(
            text("SELECT 1 FROM usuarios WHERE LOWER(TRIM(email)) = LOWER(TRIM(:e))"),
            {"e": payload.email},
        ).fetchone()

        if exists:
            raise HTTPException(status_code=409, detail="Email ya existe")

        new_id = str(uuid4())

        self.db.execute(
            text("""
                INSERT INTO usuarios (
                    id,
                    email,
                    nombre,
                    password_hash,
                    rol,
                    area,
                    telefono,
                    is_active
                )
                VALUES (
                    :id,
                    :email,
                    :nombre,
                    :ph,
                    :rol,
                    :area,
                    :telefono,
                    true
                )
            """),
            {
                "id": new_id,
                "email": payload.email.strip(),
                "nombre": payload.nombre.strip(),
                "ph": hash_password(payload.password),
                "rol": payload.rol,
                "area": payload.area,
                "telefono": payload.telefono.strip() if payload.telefono else None,
            },
        )
        self.db.commit()

        return {"message": "Usuario creado", "id": new_id}

    def list_users(self):
        rows = (
            self.db.execute(
                text("""
                    SELECT
                        id,
                        email,
                        nombre,
                        rol,
                        area,
                        telefono,
                        is_active
                    FROM usuarios
                    ORDER BY nombre ASC
                """)
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]

    def update_user(self, user_id: str, payload):
        row = self.db.execute(
            text("SELECT id FROM usuarios WHERE id=:id"),
            {"id": user_id},
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Usuario no existe")

        fields = []
        params = {"id": user_id}

        if payload.email is not None:
            fields.append("email=:email")
            params["email"] = payload.email.strip()

        if payload.nombre is not None:
            fields.append("nombre=:nombre")
            params["nombre"] = payload.nombre.strip()

        if payload.rol is not None:
            fields.append("rol=:rol")
            params["rol"] = payload.rol

        if payload.area is not None:
            fields.append("area=:area")
            params["area"] = payload.area

        if payload.telefono is not None:
            fields.append("telefono=:telefono")
            params["telefono"] = payload.telefono.strip() if payload.telefono else None

        if payload.is_active is not None:
            fields.append("is_active=:is_active")
            params["is_active"] = payload.is_active

        if payload.password is not None and payload.password.strip():
            fields.append("password_hash=:ph")
            params["ph"] = hash_password(payload.password.strip())

        if not fields:
            return {"message": "Nada para actualizar"}

        sql = "UPDATE usuarios SET " + ", ".join(fields) + " WHERE id=:id"

        self.db.execute(text(sql), params)
        self.db.commit()

        return {"message": "Usuario actualizado"}

    def delete_user(self, user_id: str):
        self.db.execute(
            text("DELETE FROM usuarios WHERE id=:id"),
            {"id": user_id},
        )
        self.db.commit()
        return {"message": "Usuario eliminado"}
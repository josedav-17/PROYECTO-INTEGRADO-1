from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

Role = Literal["ADMIN", "MESA", "AREA", "USUARIO"]

class UserCreateIn(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=2)
    password: str = Field(min_length=6)
    rol: Role
    area: Optional[str] = None
    telefono: Optional[str] = Field(default=None, max_length=30)

class UserUpdateIn(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    rol: Optional[Role] = None
    area: Optional[str] = None
    telefono: Optional[str] = Field(default=None, max_length=30)
    password: Optional[str] = Field(default=None, min_length=6)
    is_active: Optional[bool] = None
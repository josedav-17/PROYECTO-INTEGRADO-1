from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

Role = Literal["ADMIN", "MESA", "AREA", "USUARIO"]

class UserCreateIn(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=2)
    password: str = Field(min_length=6)
    rol: Role
    area: Optional[str] = None

class UserUpdateIn(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    rol: Optional[Role] = None
    area: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)
    is_active: Optional[bool] = None
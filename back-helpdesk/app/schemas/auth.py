from pydantic import BaseModel, EmailStr

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class LoginUserOut(BaseModel):
    id: str
    email: EmailStr
    rol: str
    area: str | None = None
    nombre: str

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserOut
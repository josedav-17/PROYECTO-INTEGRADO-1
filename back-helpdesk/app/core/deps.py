from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.config import JWT_SECRET, JWT_ALG
from app.core.security import decode_token

bearer = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    token = creds.credentials
    try:
        payload = decode_token(token, JWT_SECRET, JWT_ALG)
        return payload  # sub, rol, area, email, nombre...
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def require_roles(*roles: str):
    def _guard(user: dict = Depends(get_current_user)) -> dict:
        if user.get("rol") not in roles:
            raise HTTPException(status_code=403, detail="Sin permisos")
        return user
    return _guard
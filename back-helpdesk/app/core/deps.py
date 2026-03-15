from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.config import SECRET_KEY, ALGORITHM
from app.core.security import decode_token

security = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return decode_token(creds.credentials, SECRET_KEY, ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expiradoAAAAAAAAAAAAAAA")

def require_roles(*allowed_roles: str):
    def _dep(user: dict = Depends(get_current_user)):
        rol = user.get("rol")
        if rol not in allowed_roles:
            raise HTTPException(status_code=403, detail="No autorizadoAAAAAAAAAAAAAAA")
        return user
    return _dep
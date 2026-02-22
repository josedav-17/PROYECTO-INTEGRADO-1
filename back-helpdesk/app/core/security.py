from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(payload: dict, secret: str, alg: str, expires_delta):
    now = datetime.now(timezone.utc)
    exp = now + expires_delta
    to_encode = {**payload, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(to_encode, secret, algorithm=alg)

def decode_token(token: str, secret: str, alg: str) -> dict:
    return jwt.decode(token, secret, algorithms=[alg])
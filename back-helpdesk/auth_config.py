import os
from datetime import timedelta

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-cambia-esto")
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=8)
import bcrypt, os
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        return None


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> str:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credential_error

    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise credential_error

    return user

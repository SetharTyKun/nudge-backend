from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.models import User
from app.database import get_session
from app.schemas import UserCreate, UserResponse, Token, GoogleLoginRequest
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_google_token,
)
from app.dependencies import get_current_user
import secrets

router = APIRouter()


# Register
@router.post("/register", status_code=201, response_model=UserResponse)
async def register(
    user_in: UserCreate, session: Session = Depends(get_session)
) -> UserResponse:
    existing_username = session.exec(
        select(User).where(User.username == user_in.username.lower())
    ).first()

    if existing_username:
        raise HTTPException(status_code=409, detail="Username already taken")

    existing_email = session.exec(
        select(User).where(User.email == user_in.email.lower())
    ).first()

    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        username=user_in.username.lower(),
        email=user_in.email.lower(),
        hashed_password=hash_password(user_in.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:

    user = session.exec(
        select(User).where(User.username == form_data.username.lower())
    ).first()

    if not user:
        user = session.exec(
            select(User).where(User.email == form_data.username.lower())
        ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user_id=user.id)

    return Token(access_token=token)


@router.post("/google-login", response_model=Token)
async def google_login(
    request: GoogleLoginRequest, session: Session = Depends(get_session)
):
    try:
        id_info = verify_google_token(request.id_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Token")

    email = id_info.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Google account has no email")

    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        user = User(
            username=email.split("@")[0],
            email=email,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    token = create_access_token(user.id)
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

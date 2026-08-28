from fastapi import FastAPI, Path, Query, HTTPException, Depends, APIRouter
from datetime import datetime
from app.database import create_db_and_tables, get_session
from app.models import User, Note
from app.auth import hash_password, verify_password, create_access_token
from sqlmodel import Session, select
from app.schemas import (
    NoteCreate,
    NoteListResponse,
    NoteResponse,
    NoteUpdate,
    UserCreate,
    UserResponse,
    Token,
)
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_current_user
import fastapi_swagger_dark as fsd
from app.routers import users, notes


app = FastAPI(title="Notes API", version="1.0.0", docs_url=None)

# make /docs to dark theme
dark_docs_router = APIRouter()
fsd.install(dark_docs_router)
app.include_router(dark_docs_router)


# run exaclty once after the server first starts
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Authenication
app.include_router(users.router, prefix="/users", tags=["users"])

# Notes
app.include_router(notes.router, prefix="/notes", tags=["notes"])

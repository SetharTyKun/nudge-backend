from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.dependencies import get_current_user
from app.schemas import (
    NoteCreate,
    NoteResponse,
    NoteUpdate,
    NoteListResponse,
)
from app.models import Note, User, utc_now
from app.database import get_session


router = APIRouter()


# Create note
@router.post("/", status_code=201, response_model=NoteResponse)
async def create_note(
    note_in: NoteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    note = Note(**note_in.model_dump(), owner_id=current_user.id)

    session.add(note)
    session.commit()
    session.refresh(note)

    return note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = session.get(Note, note_id)

    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_in: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = session.get(Note, note_id)

    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    # exclude_unset=True means if note_in = {"title": None, "content": None, "is_pinnned": True}, then changes = {"is_pinned": True}
    changes = note_in.model_dump(exclude_unset=True)

    for key, value in changes.items():
        setattr(note, key, value)

    note.updated_at = utc_now()

    session.add(note)
    session.commit()
    session.refresh(note)

    return note


# DELETE note BY ID
@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = session.get(Note, note_id)

    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(note)
    session.commit()


@router.get("/", response_model=NoteListResponse)
async def get_notes(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    notes = session.exec(select(Note).where(Note.owner_id == current_user.id)).all()

    if len(notes) == 0:
        return NoteListResponse(
            notes=notes,
            limit=limit,
            offset=offset,
            total=len(notes),
        )

    filtered_notes = []
    stop = min(offset + limit, len(notes))
    for i in range(offset, stop):
        filtered_notes.append(notes[i])

    return NoteListResponse(
        notes=filtered_notes,
        limit=limit,
        offset=offset,
        total=len(notes),
    )

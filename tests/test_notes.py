from app.main import app
import pytest
from sqlmodel import create_engine, Session, SQLModel
from fastapi.testclient import TestClient
from sqlmodel.pool import StaticPool
from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    client.post(
        "/users/register",
        json={
            "username": "sethartykun16",
            "email": "sethartykun16@gmail.com",
            "password": "12345678",
        },
    )

    response = client.post(
        "/users/login",
        data={
            "username": "sethartykun16",
            "password": "12345678",
        },
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_register_user(client: TestClient):
    response = client.post(
        "/users/register",
        json={
            "username": "sethartykun16",
            "email": "sethartykun16@gmail.com",
            "password": "12345678",
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert data["username"] == "sethartykun16"
    assert "id" in data
    assert data["email"] == "sethartykun16@gmail.com"
    assert "hashed_password" not in data


def test_login_user(client: TestClient):
    client.post(
        "/users/register",
        json={
            "username": "sethartykun16",
            "email": "sethartykun16@gmail.com",
            "password": "12345678",
        },
    )

    response = client.post(
        "/users/login",
        data={
            "username": "sethartykun16",
            "password": "12345678",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_create_note(client: TestClient, auth_headers: dict):
    pre_response = client.get("/users/me", headers=auth_headers)

    user_id = pre_response.json()["id"]

    response = client.post(
        "/notes/",
        headers=auth_headers,
        json={
            "title": "Greeting",
            "content": "Hello, my name is TYKUN",
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert data["title"] == "Greeting"
    assert data["owner_id"] == user_id


def test_update_note(client: TestClient):
    client.post(
        "/users/register",
        json={
            "username": "sethartykun16",
            "email": "sethartykun@gmail.com",
            "password": "12345678",
        },
    )

    response = client.post(
        "/users/login",
        data={
            "username": "sethartykun16",
            "password": "12345678",
        },
    )

    token = response.json()["access_token"]

    token_headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/notes/",
        headers=token_headers,
        json={
            "title": "FastAPI",
            "content": "Learn route and schema",
        },
    )

    note_id = response.json()["id"]

    response = client.patch(
        f"/notes/{note_id}", headers=token_headers, json={"is_pinned": True}
    )

    data = response.json()

    assert data["title"] == "FastAPI"
    assert data["content"] == "Learn route and schema"
    assert data["is_pinned"] == True

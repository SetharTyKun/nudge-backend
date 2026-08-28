from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./notes.db"

engine = create_engine(
    DATABASE_URL,
    # SQLite-only fix: lets this connection be used across FastAPI's multiple threads
    connect_args={"check_same_thread": False},
    # Prints every real SQL statement to the terminal — helpful while learning, turn off in production
    echo=True,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

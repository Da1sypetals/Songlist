import os
import uuid
from typing import List, Optional, Literal
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import jwt

# Load environment variables
load_dotenv()

# Get environment variables
db_connection_string = os.getenv("DATABASE_URL")
ADMIN_USERNAME = os.getenv("SONGLIST_USERNAME")
ADMIN_PASSWORD = os.getenv("SONGLIST_PASSWORD")
# print(ADMIN_USERNAME)
# print(ADMIN_PASSWORD)

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_WEEKS = 99999

app = FastAPI(title="Song Manager API")


# Add CORS middleware here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth Models
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Security
security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(weeks=JWT_EXPIRATION_WEEKS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# Auth Routes
@app.post("/login", response_model=Token)
async def login(login_request: LoginRequest):
    if (
        login_request.username != ADMIN_USERNAME
        or login_request.password != ADMIN_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": ADMIN_USERNAME})
    return {"access_token": access_token, "token_type": "bearer"}


# Models
class SongBase(BaseModel):
    name: str
    singers: List[str]
    tags: List[str]
    links: List[str]

    @field_validator("singers")
    @classmethod
    def singers_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Singers list cannot be empty")
        return list(set(v))  # Remove duplicates

    @field_validator("tags", "links")
    @classmethod
    def remove_duplicates(cls, v):
        return list(set(v))  # Remove duplicates


class SongCreate(SongBase):
    pass


class SongUpdate(BaseModel):
    uuid: str
    name: Optional[str] = None
    singers: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    links: Optional[List[str]] = None

    @field_validator("singers")
    @classmethod
    def singers_not_empty_if_provided(cls, v):
        if v is not None and not v:
            raise ValueError("Singers list cannot be empty")
        if v is not None:
            return list(set(v))  # Remove duplicates
        return v

    @field_validator("tags", "links")
    @classmethod
    def remove_duplicates_if_provided(cls, v):
        if v is not None:
            return list(set(v))  # Remove duplicates
        return v


class Song(SongBase):
    uuid: str


class MoveSongs(BaseModel):
    moveto: Literal["todo-songs", "songs-todo"]
    uuids: List[str]


# Database functions
def get_db_connection():
    conn = psycopg2.connect(db_connection_string, cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn


def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


# Routes
@app.get("/songs/", response_model=List[Song])
async def get_songs(db: psycopg2.extensions.connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT uuid, data FROM songs")
    results = cursor.fetchall()
    cursor.close()

    songs = []
    for row in results:
        song_data = row["data"]
        song_data["uuid"] = str(row["uuid"])
        songs.append(Song(**song_data))

    return songs


@app.get("/todo/", response_model=List[Song])
async def get_todo_songs(db: psycopg2.extensions.connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT uuid, data FROM todo_songs")
    results = cursor.fetchall()
    cursor.close()

    songs = []
    for row in results:
        song_data = row["data"]
        song_data["uuid"] = str(row["uuid"])
        songs.append(Song(**song_data))

    return songs


@app.post("/songs/new/", response_model=Song)
async def create_song(
    song: SongCreate,
    db: psycopg2.extensions.connection = Depends(get_db),
    _: dict = Depends(verify_token),
):
    song_uuid = str(uuid.uuid4())
    song_data = song.model_dump()

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO songs (uuid, data) VALUES (%s, %s)", (song_uuid, Json(song_data))
    )
    cursor.close()

    return {**song_data, "uuid": song_uuid}


@app.post("/todo/new/", response_model=Song)
async def create_todo_song(
    song: SongCreate,
    db: psycopg2.extensions.connection = Depends(get_db),
    _: dict = Depends(verify_token),
):
    song_uuid = str(uuid.uuid4())
    song_data = song.model_dump()

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO todo_songs (uuid, data) VALUES (%s, %s)",
        (song_uuid, Json(song_data)),
    )
    cursor.close()

    return {**song_data, "uuid": song_uuid}


@app.post("/songs/update/", response_model=Song)
async def update_song(
    song_update: SongUpdate,
    db: psycopg2.extensions.connection = Depends(get_db),
    _: dict = Depends(verify_token),
):
    # First, get the existing song
    cursor = db.cursor()
    cursor.execute("SELECT data FROM songs WHERE uuid = %s", (song_update.uuid,))
    result = cursor.fetchone()

    if not result:
        # Check if it's in todo_songs
        cursor.execute(
            "SELECT data FROM todo_songs WHERE uuid = %s", (song_update.uuid,)
        )
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Song not found")

        table_name = "todo_songs"
    else:
        table_name = "songs"

    # Update the song data
    existing_data = result["data"]

    update_data = song_update.model_dump(exclude_unset=True)
    song_uuid = update_data.pop("uuid")

    # Merge updates with existing data
    for key, value in update_data.items():
        if value is not None:  # Only update fields that were provided
            existing_data[key] = value

    # Save updated data
    cursor.execute(
        f"UPDATE {table_name} SET data = %s WHERE uuid = %s",
        (Json(existing_data), song_uuid),
    )
    cursor.close()

    return {**existing_data, "uuid": song_uuid}


@app.post("/todo/update/", response_model=Song)
async def update_todo_song(
    song_update: SongUpdate,
    db: psycopg2.extensions.connection = Depends(get_db),
    _: dict = Depends(verify_token),
):
    # Get the existing song from todo_songs
    cursor = db.cursor()
    cursor.execute("SELECT data FROM todo_songs WHERE uuid = %s", (song_update.uuid,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Todo song not found")

    # Update the song data
    existing_data = result["data"]

    update_data = song_update.model_dump(exclude_unset=True)
    song_uuid = update_data.pop("uuid")

    # Merge updates with existing data
    for key, value in update_data.items():
        if value is not None:  # Only update fields that were provided
            existing_data[key] = value

    # Save updated data
    cursor.execute(
        "UPDATE todo_songs SET data = %s WHERE uuid = %s",
        (Json(existing_data), song_uuid),
    )
    cursor.close()

    return {**existing_data, "uuid": song_uuid}


@app.post("/move/")
async def move_songs(
    move_request: MoveSongs,
    db: psycopg2.extensions.connection = Depends(get_db),
    _: dict = Depends(verify_token),
):
    not_found = []

    if move_request.moveto == "todo-songs":
        source_table = "songs"
        target_table = "todo_songs"
    elif move_request.moveto == "songs-todo":
        source_table = "todo_songs"
        target_table = "songs"
    else:
        raise HTTPException(status_code=400, detail="Invalid moveto value")

    cursor = db.cursor()

    for song_uuid in move_request.uuids:
        # Get the song from the source table
        cursor.execute(f"SELECT data FROM {source_table} WHERE uuid = %s", (song_uuid,))
        result = cursor.fetchone()

        if not result:
            not_found.append(song_uuid)
            continue

        song_data = result["data"]

        # Insert the song into the target table
        cursor.execute(
            f"INSERT INTO {target_table} (uuid, data) VALUES (%s, %s) ON CONFLICT (uuid) DO UPDATE SET data = %s",
            (song_uuid, Json(song_data), Json(song_data)),
        )

        # Delete the song from the source table
        cursor.execute(f"DELETE FROM {source_table} WHERE uuid = %s", (song_uuid,))

    cursor.close()

    if not_found:
        return {"not_found": not_found}
    else:
        return {"status": "ok"}


# New delete endpoints
class DeleteRequest(BaseModel):
    uuids: List[str]


@app.post("/songs/delete/")
async def delete_songs(
    delete_request: DeleteRequest,
    db: psycopg2.extensions.connection = Depends(get_db),
    _: dict = Depends(verify_token),
):
    cursor = db.cursor()
    not_found = []

    for song_uuid in delete_request.uuids:
        cursor.execute("SELECT 1 FROM songs WHERE uuid = %s", (song_uuid,))
        if not cursor.fetchone():
            not_found.append(song_uuid)
        else:
            cursor.execute("DELETE FROM songs WHERE uuid = %s", (song_uuid,))

    cursor.close()

    if not_found:
        return {"not_found": not_found}
    return {"status": "ok"}


@app.post("/todo/delete/")
async def delete_todo_songs(
    delete_request: DeleteRequest,
    db: psycopg2.extensions.connection = Depends(get_db),
    _: dict = Depends(verify_token),
):
    cursor = db.cursor()
    not_found = []

    for song_uuid in delete_request.uuids:
        cursor.execute("SELECT 1 FROM todo_songs WHERE uuid = %s", (song_uuid,))
        if not cursor.fetchone():
            not_found.append(song_uuid)
        else:
            cursor.execute("DELETE FROM todo_songs WHERE uuid = %s", (song_uuid,))

    cursor.close()

    if not_found:
        return {"not_found": not_found}
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

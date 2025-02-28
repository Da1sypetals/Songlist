import os
import uuid
import random
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection string
db_connection_string = os.getenv("DATABASE_URL")

# Sample data for mock songs
sample_song_names = [
    "Bohemian Rhapsody",
    "Hotel California",
    "Imagine",
    "Sweet Child O' Mine",
    "Smells Like Teen Spirit",
    "Stairway to Heaven",
    "Wonderwall",
    "Billie Jean",
    "Like a Rolling Stone",
    "Hey Jude",
    "Hallelujah",
    "Yesterday",
    "Every Breath You Take",
    "Thriller",
    "Blowin' in the Wind",
    "Creep",
    "Purple Haze",
    "Let It Be",
    "What's Going On",
    "Respect",
    "Shake It Off",
    "Bad Guy",
    "Someone Like You",
    "Uptown Funk",
    "Lose Yourself",
    "Hello",
    "Shape of You",
    "Despacito",
    "All I Want for Christmas Is You",
    "Don't Stop Believin'",
    "Dancing Queen",
    "Livin' on a Prayer",
    "Sweet Home Alabama",
    "Boogie Wonderland",
    "Africa",
    "Take On Me",
    "Eye of the Tiger",
    "Smooth Criminal",
    "Viva la Vida",
    "Poker Face",
    "Counting Stars",
    "Royals",
    "Highway to Hell",
    "Paradise City",
    "Nothing Else Matters",
    "Enter Sandman",
]

sample_singers = [
    "Queen",
    "Eagles",
    "John Lennon",
    "Guns N' Roses",
    "Nirvana",
    "Led Zeppelin",
    "Oasis",
    "Michael Jackson",
    "Bob Dylan",
    "The Beatles",
    "Leonard Cohen",
    "Jeff Buckley",
    "The Police",
    "Radiohead",
    "Jimi Hendrix",
    "Marvin Gaye",
    "Adele",
    "Bruno Mars",
    "Lady Gaga",
    "Ed Sheeran",
    "Taylor Swift",
    "Ariana Grande",
    "Justin Bieber",
    "Billie Eilish",
    "Beyoncé",
    "Elton John",
    "Freddie Mercury",
    "Whitney Houston",
    "Frank Sinatra",
    "Elvis Presley",
    "Johnny Cash",
    "Aretha Franklin",
    "David Bowie",
    "Prince",
    "Madonna",
    "Bob Marley",
    "U2",
    "Coldplay",
    "Pink Floyd",
    "The Rolling Stones",
    "AC/DC",
    "Metallica",
    "Linkin Park",
    "Green Day",
    "Red Hot Chili Peppers",
    "Foo Fighters",
]

sample_tags = [
    "rock",
    "pop",
    "indie",
    "alternative",
    "classic rock",
    "blues",
    "jazz",
    "r&b",
    "soul",
    "folk",
    "country",
    "electronic",
    "dance",
    "metal",
    "punk",
    "hip-hop",
    "rap",
    "reggae",
    "acoustic",
    "instrumental",
    "ballad",
    "love song",
    "breakup song",
    "upbeat",
    "sad",
    "energetic",
    "easy",
    "intermediate",
    "advanced",
    "favorite",
    "party",
    "karaoke",
    "wedding",
    "emotional",
    "feel-good",
    "nostalgic",
    "anthem",
    "chill",
    "workout",
    "driving",
    "90s",
    "80s",
    "70s",
    "60s",
    "00s",
    "10s",
    "fast",
    "slow",
    "epic",
    "catchy",
    "summer",
    "winter",
]

sample_links = [
    "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",  # Bohemian Rhapsody
    "https://www.youtube.com/watch?v=BciS5krYL80",  # Hotel California
    "https://www.youtube.com/watch?v=YkgkThdzX-8",  # Imagine
    "https://www.youtube.com/watch?v=1w7OgIMMRc4",  # Sweet Child O' Mine
    "https://www.youtube.com/watch?v=hTWKbfoikeg",  # Smells Like Teen Spirit
    "https://www.youtube.com/watch?v=QkF3oxziUI4",  # Stairway to Heaven
    "https://www.youtube.com/watch?v=bx1Bh8ZvH84",  # Wonderwall
    "https://www.youtube.com/watch?v=Zi_XLOBDo_Y",  # Billie Jean
    "https://www.youtube.com/watch?v=IwOfCgkyEj0",  # Like a Rolling Stone
    "https://www.youtube.com/watch?v=A_MjCqQoLLA",  # Hey Jude
    "https://open.spotify.com/track/3WgZqYzKxnxipJK3p9Pw2D",  # Bohemian Rhapsody
    "https://open.spotify.com/track/40riOy7x9W7GXjyGp4pjAv",  # Hotel California
    "https://open.spotify.com/track/7pKfPomDEeI4TPT6EOYjn9",  # Imagine
    "https://open.spotify.com/track/7o2CTH4ctstm8TNelqjb51",  # Sweet Child O' Mine
    "https://music.apple.com/us/album/bohemian-rhapsody/1440806723?i=1440806930",
    "https://music.apple.com/us/album/hotel-california/635770200?i=635770201",
    "https://music.apple.com/us/album/imagine/1440824484?i=1440824490",
    "https://music.apple.com/us/album/sweet-child-o-mine/1377813284?i=1377813291",
    "https://www.deezer.com/track/3133704",
    "https://www.deezer.com/track/1109731",
    "https://soundcloud.com/queen-official/bohemian-rhapsody",
    "https://soundcloud.com/eaglesmusic/hotel-california",
    "https://www.guitarbackingtrack.com/play/eagles/hotel_california.htm",
    "https://www.ultimate-guitar.com/search.php?title=bohemian+rhapsody",
    "https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-chords-46190",
]


def generate_song():
    """Generate a random song with mock data"""
    # Pick 1-3 singers
    num_singers = random.randint(1, 3)
    singers = random.sample(sample_singers, num_singers)

    # Pick 1-6 tags
    num_tags = random.randint(1, 6)
    tags = random.sample(sample_tags, num_tags)

    # Pick 1-4 links
    num_links = random.randint(1, 4)
    links = random.sample(sample_links, num_links)

    return {
        "name": random.choice(sample_song_names),
        "singers": singers,
        "tags": tags,
        "links": links,
    }


def insert_mock_data(num_songs=20, num_todo_songs=15):
    """Insert mock data into the database"""
    conn = psycopg2.connect(db_connection_string)
    conn.autocommit = True
    cursor = conn.cursor()

    # Insert songs
    print(f"Inserting {num_songs} songs into 'songs' table...")
    for _ in range(num_songs):
        song_data = generate_song()
        song_uuid = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO songs (uuid, data) VALUES (%s, %s)",
            (song_uuid, Json(song_data)),
        )

    # Insert todo songs
    print(f"Inserting {num_todo_songs} songs into 'todo_songs' table...")
    for _ in range(num_todo_songs):
        song_data = generate_song()
        song_uuid = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO todo_songs (uuid, data) VALUES (%s, %s)",
            (song_uuid, Json(song_data)),
        )

    cursor.close()
    conn.close()

    print("Mock data insertion complete!")


if __name__ == "__main__":
    # Check if tables exist, create them if they don't
    conn = psycopg2.connect(db_connection_string)
    cursor = conn.cursor()

    # Create songs table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        uuid UUID PRIMARY KEY,
        data JSONB NOT NULL
    );
    """)

    # Create todo_songs table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todo_songs (
        uuid UUID PRIMARY KEY,
        data JSONB NOT NULL
    );
    """)

    # Check if tables already have data
    cursor.execute("SELECT COUNT(*) FROM songs")
    songs_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM todo_songs")
    todo_count = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    if songs_count > 0 or todo_count > 0:
        print(f"Found existing data: {songs_count} songs, {todo_count} todo songs")
        response = input(
            "Would you like to clear existing data before adding mock data? (y/n): "
        )
        if response.lower() == "y":
            conn = psycopg2.connect(db_connection_string)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("TRUNCATE songs, todo_songs")
            cursor.close()
            conn.close()
            print("Existing data cleared.")
            insert_mock_data(30, 20)
        else:
            print("Adding mock data to existing tables...")
            insert_mock_data(30, 20)
    else:
        # Insert mock data
        insert_mock_data(30, 20)

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection string from environment variables
db_connection_string = os.getenv("DATABASE_URL")


def drop_all_tables(conn, cur):
    """
    Drop all tables in the database.
    """
    # Get a list of all tables in the database
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)
    tables = cur.fetchall()

    # Drop each table
    for table in tables:
        table_name = table[0]
        cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        print(f"Dropped table: {table_name}")

    # Commit the transaction
    conn.commit()


def create_tables():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(db_connection_string)

    # Create a cursor object
    cur = conn.cursor()

    # Drop all existing tables
    drop_all_tables(conn, cur)

    # Create songs table
    cur.execute("""
    CREATE TABLE songs (
        uuid UUID PRIMARY KEY,
        data JSONB NOT NULL
    );
    """)

    # Create todo_songs table
    cur.execute("""
    CREATE TABLE todo_songs (
        uuid UUID PRIMARY KEY,
        data JSONB NOT NULL
    );
    """)

    # Commit the transaction
    conn.commit()

    # Close cursor and connection
    cur.close()
    conn.close()

    print("Tables created successfully!")


if __name__ == "__main__":
    create_tables()

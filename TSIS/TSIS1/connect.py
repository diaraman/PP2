import psycopg2
import os
from config import load_config


def get_connection():
    # This helper opens a brand-new database connection each time it is called.
    # The app uses it for short tasks so it does not keep one connection forever.
    try:
        return psycopg2.connect(**load_config())
    except Exception as error:
        print(f"Connection error: {error}")
        return None


def setup_database():
    """
    Creates ALL tables from scratch and loads SQL files.
    Run this once before using the app.
    """
    # This function prepares the whole phonebook database schema.
    # It creates tables first, then seeds default groups, then loads SQL helpers.
    conn = None
    try:
        conn = psycopg2.connect(**load_config())
        cur = conn.cursor()

        # Step 1: create the groups table so contacts can belong to a category.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id   SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """)

        # Step 2: insert a few default groups so the menu has something to use immediately.
        cur.execute("""
            INSERT INTO groups (name)
            VALUES ('Family'), ('Work'), ('Friend'), ('Other')
            ON CONFLICT (name) DO NOTHING
        """)

        # Step 3: create the main contacts table with the basic person info.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id       SERIAL PRIMARY KEY,
                name     VARCHAR(255) NOT NULL UNIQUE,
                email    VARCHAR(100),
                birthday DATE,
                group_id INTEGER REFERENCES groups(id)
            )
        """)

        # Step 4: create the phones table because one contact can have many numbers.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id         SERIAL PRIMARY KEY,
                contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
                phone      VARCHAR(20) NOT NULL,
                type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
            )
        """)

        # Step 5: load stored procedures and helper SQL if the file exists.
        if os.path.exists('procedures.sql'):
            with open('procedures.sql', 'r', encoding='utf-8') as f:
                cur.execute(f.read())

        conn.commit()
        # Commit makes all created tables and seeded rows permanent.
        print("Database setup complete! All tables and procedures are ready.")

    except Exception as error:
        print(f"Setup error: {error}")
    finally:
        # Always close the connection so the program does not leak resources.
        if conn:
            conn.close()


if __name__ == '__main__':
    setup_database()

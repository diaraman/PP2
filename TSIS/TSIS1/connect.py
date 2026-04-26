from pathlib import Path
from config import load_config

try:
    import psycopg2
except ImportError:  # pragma: no cover - runtime dependency guard
    psycopg2 = None


BASE_DIR = Path(__file__).resolve().parent


def get_connection():
    # This helper opens a brand-new database connection each time it is called.
    # The app uses it for short tasks so it does not keep one connection forever.
    if psycopg2 is None:
        print("Missing dependency: install psycopg2-binary with `pip install -r TSIS/TSIS1/requirements.txt`.")
        return None

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
        if psycopg2 is None:
            print("Missing dependency: install psycopg2-binary with `pip install -r TSIS/TSIS1/requirements.txt`.")
            return

        conn = psycopg2.connect(**load_config())
        cur = conn.cursor()

        # Load schema and server-side logic from SQL files in this folder.
        for sql_name in ("schema.sql", "procedures.sql"):
            sql_path = BASE_DIR / sql_name
            if sql_path.exists():
                with sql_path.open("r", encoding="utf-8") as f:
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

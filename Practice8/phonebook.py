import json
from pathlib import Path

from psycopg2.extras import Json

from connect import get_connection

BASE_DIR = Path(__file__).resolve().parent
FUNCTIONS_SQL = BASE_DIR / "functions.sql"
PROCEDURES_SQL = BASE_DIR / "procedures.sql"


def run_sql_file(file_path: Path):
    # Apply raw SQL files (functions/procedures) to the current database.
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(file_path.read_text(encoding="utf-8"))
        conn.commit()
        print(f"Applied: {file_path.name}")
    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"Error applying {file_path.name}: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def create_table():
    # Base table used by all functions/procedures in this practice.
    sql = """
    CREATE TABLE IF NOT EXISTS phonebook_users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(150) NOT NULL UNIQUE,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100),
        phone VARCHAR(20) NOT NULL UNIQUE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print("Table phonebook_users is ready.")
    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"Create table error: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def setup_database_objects():
    # One setup entrypoint: table first, then SQL objects.
    create_table()
    run_sql_file(FUNCTIONS_SQL)
    run_sql_file(PROCEDURES_SQL)


def upsert_user(name: str, phone: str):
    # CALL procedure: action-oriented DB operation.
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("CALL phonebook_upsert_user(%s, %s);", (name, phone))
        conn.commit()
        print("Upsert completed.")
    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"Upsert error: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def bulk_upsert_users(names, phones):
    # Sends arrays to the bulk procedure and prints invalid rows returned by INOUT.
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL phonebook_bulk_upsert_users(%s, %s, %s::jsonb);",
            (names, phones, Json([])),
        )

        invalid = []
        if cur.description:
            row = cur.fetchone()
            if row:
                invalid = row[0]

        conn.commit()
        print("Bulk upsert completed.")
        if invalid:
            print("Invalid records:")
            print(json.dumps(invalid, indent=2, ensure_ascii=False))
        else:
            print("No invalid records.")
    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"Bulk upsert error: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def search_by_pattern(pattern: str):
    # SELECT function: read-oriented DB operation returning rows.
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM phonebook_search(%s);", (pattern,))
        rows = cur.fetchall()

        if not rows:
            print("No records found.")
            return

        for row in rows:
            print(row)
    except Exception as exc:
        print(f"Search error: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_page(limit: int, offset: int):
    # Pagination helper over function with LIMIT/OFFSET arguments.
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM phonebook_get_page(%s, %s);", (limit, offset))
        rows = cur.fetchall()

        if not rows:
            print("No records on this page.")
            return

        for row in rows:
            print(row)
    except Exception as exc:
        print(f"Pagination error: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def delete_user(username: str | None = None, phone: str | None = None):
    # Deletes by either username or phone using a stored procedure.
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("CALL phonebook_delete_user(%s, %s);", (username, phone))
        conn.commit()
        print("Delete procedure executed.")
    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"Delete error: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_total_count():
    # Scalar function example: returns one integer value.
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT phonebook_total_count();")
        count = cur.fetchone()[0]
        print(f"Total users: {count}")
    except Exception as exc:
        print(f"Count error: {exc}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def menu():
    # Simple CLI to demonstrate each requirement from the practice.
    while True:
        print("\n--- PRACTICE 8 PHONEBOOK ---")
        print("1. Setup table/functions/procedures")
        print("2. Upsert one user (CALL phonebook_upsert_user)")
        print("3. Bulk upsert users (CALL phonebook_bulk_upsert_users)")
        print("4. Search by pattern (SELECT phonebook_search)")
        print("5. Get paginated users (SELECT phonebook_get_page)")
        print("6. Delete by username or phone (CALL phonebook_delete_user)")
        print("7. Show total count (SELECT phonebook_total_count)")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            setup_database_objects()
        elif choice == "2":
            name = input("Name (e.g., John Smith): ").strip()
            phone = input("Phone (+77001234567): ").strip()
            upsert_user(name, phone)
        elif choice == "3":
            names_raw = input("Names (comma separated): ").strip()
            phones_raw = input("Phones (comma separated): ").strip()
            names = [item.strip() for item in names_raw.split(",") if item.strip()]
            phones = [item.strip() for item in phones_raw.split(",") if item.strip()]
            bulk_upsert_users(names, phones)
        elif choice == "4":
            pattern = input("Pattern: ").strip()
            search_by_pattern(pattern)
        elif choice == "5":
            limit = int(input("LIMIT: ").strip())
            offset = int(input("OFFSET: ").strip())
            get_page(limit, offset)
        elif choice == "6":
            username = input("Username (or leave empty): ").strip() or None
            phone = input("Phone (or leave empty): ").strip() or None
            delete_user(username=username, phone=phone)
        elif choice == "7":
            get_total_count()
        elif choice == "0":
            print("Bye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()

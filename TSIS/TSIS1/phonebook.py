import psycopg2
import csv
import json
import os
from connect import get_connection, setup_database


# ─────────────────────────────────────────
# Helper: print one contact row nicely
# ─────────────────────────────────────────
def print_contact(row):
    id_, name, email, birthday, group_name, phones = row
    print(f"  [{id_}] {name}")
    print(f"       Email:    {email      or '—'}")
    print(f"       Birthday: {birthday   or '—'}")
    print(f"       Group:    {group_name or '—'}")
    print(f"       Phones:   {phones     or '—'}")
    print()


# ─────────────────────────────────────────
# Helper: get or create a group, return id
# ─────────────────────────────────────────
def get_group_id(cur, group_name):
    if not group_name:
        return None
    cur.execute(
        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


# ─────────────────────────────────────────
# 1. Search by name / email / phone
#    Uses search_contacts() DB function
# ─────────────────────────────────────────
def search_all():
    query = input("Search (name / email / phone): ")
    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
        print(f"\n--- Results for '{query}' ---")
        if not rows:
            print("Nothing found.")
        for row in rows:
            print_contact(row)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 2. Filter contacts by group
# ─────────────────────────────────────────
def filter_by_group():
    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            groups = cur.fetchall()
            if not groups:
                print("No groups found.")
                return

            print("\nAvailable groups:")
            for gid, gname in groups:
                print(f"  {gid}. {gname}")

            choice = input("Enter group number or name: ")

            group_name = None
            for gid, gname in groups:
                if choice == str(gid) or choice.lower() == gname.lower():
                    group_name = gname
                    break

            if not group_name:
                print("Group not found.")
                return

            cur.execute(
                """
                SELECT c.id, c.name, c.email, c.birthday,
                       g.name,
                       STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.type)
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p  ON p.contact_id = c.id
                WHERE g.name = %s
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY c.name
                """,
                (group_name,)
            )
            rows = cur.fetchall()

        print(f"\n--- Group: {group_name} ---")
        if not rows:
            print("No contacts in this group.")
        for row in rows:
            print_contact(row)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 3. Search by email (partial match)
# ─────────────────────────────────────────
def search_by_email():
    query = input("Enter email or part of email (e.g. gmail): ")
    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.name, c.email, c.birthday,
                       g.name,
                       STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.type)
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p  ON p.contact_id = c.id
                WHERE c.email ILIKE %s
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY c.name
                """,
                (f"%{query}%",)
            )
            rows = cur.fetchall()
        print(f"\n--- Email search: '{query}' ---")
        if not rows:
            print("Nothing found.")
        for row in rows:
            print_contact(row)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 4. Show all contacts with sorting
# ─────────────────────────────────────────
def show_sorted():
    print("\nSort by:")
    print("  1. Name")
    print("  2. Birthday")
    print("  3. Date added (ID)")
    choice = input("Choose [1]: ") or "1"

    sort_map = {"1": "c.name", "2": "c.birthday", "3": "c.id"}
    sort_col = sort_map.get(choice, "c.name")

    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT c.id, c.name, c.email, c.birthday,
                       g.name,
                       STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.type)
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p  ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY {sort_col} NULLS LAST
                """
            )
            rows = cur.fetchall()
        print("\n--- All contacts ---")
        if not rows:
            print("No contacts found.")
        for row in rows:
            print_contact(row)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 5. Browse contacts page by page
#    Uses get_contacts_paginated() DB function
# ─────────────────────────────────────────
def browse_pages():
    PAGE = 3
    offset = 0

    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM contacts")
            total = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        conn.close()
        return

    if total == 0:
        print("No contacts in the database.")
        return

    while True:
        conn = get_connection()
        if not conn: return
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_paginated(%s, %s)",
                    (PAGE, offset)
                )
                rows = cur.fetchall()
            conn.close()
        except Exception as e:
            print(f"Error: {e}")
            conn.close()
            return

        page_num    = offset // PAGE + 1
        total_pages = (total + PAGE - 1) // PAGE

        print(f"\n--- Page {page_num} of {total_pages}  (total: {total} contacts) ---")
        for row in rows:
            print_contact(row)

        options = []
        if offset + PAGE < total:
            options.append("[n]ext")
        if offset > 0:
            options.append("[p]rev")
        options.append("[q]uit")

        cmd = input(" | ".join(options) + ": ").lower().strip()

        if   cmd == "n" and offset + PAGE < total:
            offset += PAGE
        elif cmd == "p" and offset > 0:
            offset -= PAGE
        elif cmd in ("q", "quit", ""):
            break


# ─────────────────────────────────────────
# 6. Add phone number to a contact
#    Calls add_phone() stored procedure
# ─────────────────────────────────────────
def add_phone():
    name  = input("Contact name: ")
    phone = input("Phone number: ")
    print("Type:  1=mobile  2=home  3=work")
    t = input("Choose [1]: ") or "1"
    types = {"1": "mobile", "2": "home", "3": "work"}
    phone_type = types.get(t, "mobile")

    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        print("Done! Phone added.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 7. Move contact to a group
#    Calls move_to_group() stored procedure
# ─────────────────────────────────────────
def move_to_group():
    name       = input("Contact name: ")
    group_name = input("Group name (Family / Work / Friend / Other): ")

    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        print(f"Done! '{name}' moved to group '{group_name}'.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 8. Import from CSV (with new fields)
# ─────────────────────────────────────────
def import_csv():
    filepath = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    inserted = 0
    skipped  = 0

    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            with open(filepath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("name", "").strip()
                    if not name:
                        skipped += 1
                        continue

                    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                    if cur.fetchone():
                        print(f"  Skip (already exists): {name}")
                        skipped += 1
                        continue

                    group_id = get_group_id(cur, row.get("group", "").strip())
                    birthday = row.get("birthday", "").strip() or None
                    email    = row.get("email",    "").strip() or None

                    cur.execute(
                        "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
                        (name, email, birthday, group_id)
                    )
                    cid = cur.fetchone()[0]

                    phone_val  = row.get("phone", "").strip()
                    phone_type = row.get("type",  "mobile").strip() or "mobile"
                    if phone_val:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, phone_val, phone_type)
                        )
                    inserted += 1

        conn.commit()
        print(f"\nDone! Inserted: {inserted}, Skipped: {skipped}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 9. Import from JSON
#    On duplicate: ask skip or overwrite
# ─────────────────────────────────────────
def import_json():
    filepath = input("JSON file path [contacts_export.json]: ").strip() or "contacts_export.json"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        records = json.load(f)

    inserted = 0
    skipped  = 0
    updated  = 0

    conn = get_connection()
    if not conn: return
    try:
        with conn, conn.cursor() as cur:
            for rec in records:
                name = rec.get("name", "").strip()
                if not name:
                    skipped += 1
                    continue

                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                existing = cur.fetchone()

                if existing:
                    print(f"\nDuplicate found: '{name}'")
                    action = input("  [s]kip or [o]verwrite? ").lower()
                    if action != "o":
                        skipped += 1
                        continue

                    cid      = existing[0]
                    group_id = get_group_id(cur, rec.get("group"))
                    cur.execute(
                        "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                        (rec.get("email"), rec.get("birthday"), group_id, cid)
                    )
                    cur.execute("DELETE FROM phones WHERE contact_id = %s", (cid,))
                    updated += 1
                else:
                    group_id = get_group_id(cur, rec.get("group"))
                    cur.execute(
                        "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
                        (name, rec.get("email"), rec.get("birthday"), group_id)
                    )
                    cid = cur.fetchone()[0]
                    inserted += 1

                for ph in rec.get("phones", []):
                    p_val  = ph.get("phone", "").strip()
                    p_type = ph.get("type", "mobile")
                    if p_val:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, p_val, p_type)
                        )

        conn.commit()
        print(f"\nDone! Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# 10. Export all contacts to JSON
# ─────────────────────────────────────────
def export_json():
    filepath = input("Save as [contacts_export.json]: ").strip() or "contacts_export.json"

    conn = get_connection()
    if not conn: return
    try:
        records = []
        with conn, conn.cursor() as cur:
            cur.execute("SELECT id, name, email, birthday, group_id FROM contacts ORDER BY name")
            contacts = cur.fetchall()

            for cid, name, email, birthday, group_id in contacts:
                group_name = None
                if group_id:
                    cur.execute("SELECT name FROM groups WHERE id = %s", (group_id,))
                    g = cur.fetchone()
                    group_name = g[0] if g else None

                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY type",
                    (cid,)
                )
                phones = [{"phone": r[0], "type": r[1]} for r in cur.fetchall()]

                records.append({
                    "name":     name,
                    "email":    email,
                    "birthday": birthday.isoformat() if birthday else None,
                    "group":    group_name,
                    "phones":   phones
                })

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        print(f"Done! {len(records)} contacts exported to '{filepath}'.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────
def main():
    print("\n=== PhoneBook TSIS 1 ===")
    print("First time? Choose 0 to set up the database.\n")

    while True:
        print("--- MENU ---")
        print("0.  Setup database (run once)")
        print("--- Search & Filter ---")
        print("1.  Search by name / email / phone")
        print("2.  Filter by group")
        print("3.  Search by email")
        print("4.  Show all contacts (sorted)")
        print("5.  Browse page by page")
        print("--- Phone & Group ---")
        print("6.  Add phone number to contact")
        print("7.  Move contact to group")
        print("--- Import / Export ---")
        print("8.  Import from CSV")
        print("9.  Import from JSON")
        print("10. Export to JSON")
        print("11. Exit")

        choice = input("\nChoose: ").strip()

        if   choice == "0":  setup_database()
        elif choice == "1":  search_all()
        elif choice == "2":  filter_by_group()
        elif choice == "3":  search_by_email()
        elif choice == "4":  show_sorted()
        elif choice == "5":  browse_pages()
        elif choice == "6":  add_phone()
        elif choice == "7":  move_to_group()
        elif choice == "8":  import_csv()
        elif choice == "9":  import_json()
        elif choice == "10": export_json()
        elif choice == "11":
            print("Goodbye!")
            break
        else:
            print("Wrong choice, try again.")


if __name__ == '__main__':
    main()

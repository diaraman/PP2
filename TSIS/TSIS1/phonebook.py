import csv  # Read CSV files for import.
import json  # Read and write JSON files for import/export.
import os  # Check if files exist before opening them.
from pathlib import Path  # Build file paths relative to this script.
from connect import get_connection, setup_database  # Reuse DB helpers from connect.py.

# This is the folder where phonebook.py lives.
BASE_DIR = Path(__file__).resolve().parent


# Print one contact in a readable multi-line format.
def print_contact(row):
    # Unpack the row returned by PostgreSQL.
    id_, name, email, birthday, group_name, phones = row
    # Show the contact ID and name first.
    print(f"  [{id_}] {name}")
    # Show email, or a dash if the value is missing.
    print(f"       Email:    {email      or '—'}")
    # Show birthday, or a dash if the value is missing.
    print(f"       Birthday: {birthday   or '—'}")
    # Show group name, or a dash if the value is missing.
    print(f"       Group:    {group_name or '—'}")
    # Show all phones, or a dash if there are none.
    print(f"       Phones:   {phones     or '—'}")
    # Add a blank line between contacts.
    print()


# Return a group ID, creating the group first if needed.
def get_group_id(cur, group_name):
    # If the CSV or JSON row has no group, keep it empty.
    if not group_name:
        return None
    # Insert the group name if it does not already exist.
    cur.execute(
        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    # Look up the ID for that group name.
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    # Read one row from the result.
    row = cur.fetchone()
    # Return the ID if we found it, otherwise return None.
    return row[0] if row else None


# Search the database by the user-entered query.
def search_all():
    # Ask the user for the search text.
    query = input("Search (name / email / phone): ")
    # Open a database connection.
    conn = get_connection()
    # Stop immediately if the connection failed.
    if not conn: return
    try:
        # Use a cursor to run SQL and fetch results.
        with conn, conn.cursor() as cur:
            # search_contacts() is defined in procedures.sql.
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            # Read all matching rows.
            rows = cur.fetchall()
        # Show the search query back to the user.
        print(f"\n--- Results for '{query}' ---")
        # If nothing matched, say so clearly.
        if not rows:
            print("Nothing found.")
        # Print each matching contact.
        for row in rows:
            print_contact(row)
    except Exception as e:
        # Any SQL or runtime error is shown here.
        print(f"Error: {e}")
    finally:
        # Always close the DB connection.
        conn.close()


# Show only contacts inside one selected group.
def filter_by_group():
    # Open a DB connection.
    conn = get_connection()
    # Stop if no connection is available.
    if not conn: return
    try:
        # Run SQL inside a managed transaction block.
        with conn, conn.cursor() as cur:
            # Get all groups so the user can choose one.
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            # Read the full list of groups.
            groups = cur.fetchall()
            # If no groups exist, there is nothing to filter.
            if not groups:
                print("No groups found.")
                return

            # Show the available groups to the user.
            print("\nAvailable groups:")
            # Print each group ID and name.
            for gid, gname in groups:
                print(f"  {gid}. {gname}")

            # Ask the user to choose by number or by name.
            choice = input("Enter group number or name: ")

            # This will store the chosen group name.
            group_name = None
            # Search the list for a matching group.
            for gid, gname in groups:
                # Match either the numeric ID or the text name.
                if choice == str(gid) or choice.lower() == gname.lower():
                    group_name = gname
                    break

            # If nothing matched, stop here.
            if not group_name:
                print("Group not found.")
                return

            # Query all contacts that belong to the chosen group.
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
            # Load all matching contact rows.
            rows = cur.fetchall()

        # Show which group was selected.
        print(f"\n--- Group: {group_name} ---")
        # If the group is empty, tell the user.
        if not rows:
            print("No contacts in this group.")
        # Print each contact in the selected group.
        for row in rows:
            print_contact(row)
    except Exception as e:
        # Print any DB or runtime error.
        print(f"Error: {e}")
    finally:
        # Close the connection no matter what happened.
        conn.close()


# Search only by email, using partial matching.
def search_by_email():
    # Ask for the search fragment.
    query = input("Enter email or part of email (e.g. gmail): ")
    # Open the DB connection.
    conn = get_connection()
    # Stop if the connection is not available.
    if not conn: return
    try:
        # Run the query inside a cursor block.
        with conn, conn.cursor() as cur:
            # Search contacts with email that contains the fragment.
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
            # Read the rows returned by the query.
            rows = cur.fetchall()
        # Print a helpful heading.
        print(f"\n--- Email search: '{query}' ---")
        # If no rows matched, say so.
        if not rows:
            print("Nothing found.")
        # Print each matched contact.
        for row in rows:
            print_contact(row)
    except Exception as e:
        # Show the error instead of crashing.
        print(f"Error: {e}")
    finally:
        # Close the DB connection.
        conn.close()


# Show every contact and let the user choose the sort order.
def show_sorted():
    # Explain the available sort options.
    print("\nSort by:")
    print("  1. Name")
    print("  2. Birthday")
    print("  3. Date added (ID)")
    # Default to name sorting.
    choice = input("Choose [1]: ") or "1"

    # Map menu option to the actual SQL column.
    sort_map = {"1": "c.name", "2": "c.birthday", "3": "c.id"}
    # Fall back to name sorting if the input is invalid.
    sort_col = sort_map.get(choice, "c.name")

    # Open a DB connection.
    conn = get_connection()
    # Stop if the connection fails.
    if not conn: return
    try:
        # Use the connection and cursor safely.
        with conn, conn.cursor() as cur:
            # Pull all contacts and sort them dynamically.
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
            # Read all rows from the database.
            rows = cur.fetchall()
        # Print a heading for the output.
        print("\n--- All contacts ---")
        # If there are no contacts, say so.
        if not rows:
            print("No contacts found.")
        # Print each contact row.
        for row in rows:
            print_contact(row)
    except Exception as e:
        # Show any SQL problem here.
        print(f"Error: {e}")
    finally:
        # Close the connection when done.
        conn.close()


# Browse contacts with next/prev/quit navigation.
def browse_pages():
    # Number of contacts per page.
    PAGE = 3
    # Start at the first page.
    offset = 0

    # Open a DB connection.
    conn = get_connection()
    # Stop if connection is unavailable.
    if not conn: return
    try:
        # Count how many contacts exist in total.
        with conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM contacts")
            # Fetch the total count.
            total = cur.fetchone()[0]
        # Close this short-lived connection now.
        conn.close()
    except Exception as e:
        # Show any error while counting contacts.
        print(f"Error: {e}")
        # Close the connection before returning.
        conn.close()
        return

    # If there are no contacts, stop early.
    if total == 0:
        print("No contacts in the database.")
        return

    # Keep looping until the user quits.
    while True:
        # Open a fresh connection for each page.
        conn = get_connection()
        # Stop if connection fails.
        if not conn: return
        try:
            # Get one page of results from the DB function.
            with conn, conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_paginated(%s, %s)",
                    (PAGE, offset)
                )
                # Read the rows for this page.
                rows = cur.fetchall()
            # Close the page connection.
            conn.close()
        except Exception as e:
            # Show any error while loading the page.
            print(f"Error: {e}")
            # Close the connection before returning.
            conn.close()
            return

        # Compute the visible page number.
        page_num    = offset // PAGE + 1
        # Compute the total number of pages.
        total_pages = (total + PAGE - 1) // PAGE

        # Print the page header.
        print(f"\n--- Page {page_num} of {total_pages}  (total: {total} contacts) ---")
        # Print each row on the current page.
        for row in rows:
            print_contact(row)

        # Build the list of available commands.
        options = []
        # Only show next if there is another page.
        if offset + PAGE < total:
            options.append("[n]ext")
        # Only show prev if we are not on the first page.
        if offset > 0:
            options.append("[p]rev")
        # Quit is always available.
        options.append("[q]uit")

        # Ask the user what to do next.
        cmd = input(" | ".join(options) + ": ").lower().strip()

        # Move to the next page if allowed.
        if   cmd == "n" and offset + PAGE < total:
            offset += PAGE
        # Move to the previous page if allowed.
        elif cmd == "p" and offset > 0:
            offset -= PAGE
        # Stop the loop if the user quits.
        elif cmd in ("q", "quit", ""):
            break


# Add a brand-new contact, with optional email, birthday, group, and first phone.
def add_contact():
    # Ask for the contact name.
    name = input("Contact name: ").strip()
    # Do not allow an empty name.
    if not name:
        print("Name cannot be empty.")
        return

    # Ask for optional contact details.
    email = input("Email (optional): ").strip() or None
    birthday = input("Birthday YYYY-MM-DD (optional): ").strip() or None
    group_name = input("Group (Family / Work / Friend / Other, optional): ").strip()
    phone = input("Phone number (optional): ").strip()

    # Ask for the phone type only if a phone number was entered.
    phone_type = None
    if phone:
        print("Type:  1=mobile  2=home  3=work")
        t = input("Choose [1]: ") or "1"
        types = {"1": "mobile", "2": "home", "3": "work"}
        phone_type = types.get(t, "mobile")

    # Open the DB connection.
    conn = get_connection()
    # Stop if connection is unavailable.
    if not conn: return
    try:
        # Insert the new contact and optional phone inside one transaction.
        with conn, conn.cursor() as cur:
            # Create or find the group first.
            group_id = get_group_id(cur, group_name)
            # Check whether a contact with this name already exists.
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            # If the name already exists, let the user decide what to do.
            if existing:
                print(f"Contact '{name}' already exists.")
                action = input("  [s]kip or [u]pdate? ").strip().lower()
                if action != "u":
                    print("Skipped.")
                    return

                # Update the existing contact instead of inserting a duplicate row.
                contact_id = existing[0]
                cur.execute(
                    "UPDATE contacts SET email = %s, birthday = %s, group_id = %s WHERE id = %s",
                    (email, birthday, group_id, contact_id)
                )
            else:
                # Insert the contact row and get its ID back.
                cur.execute(
                    "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id",
                    (name, email, birthday, group_id)
                )
                # Read the new contact ID.
                contact_id = cur.fetchone()[0]

            # Save the first phone number if one was provided.
            if phone:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, phone, phone_type)
                )

        # Save the new or updated contact in the database.
        conn.commit()
        # Tell the user the contact was created or updated.
        print(f"Done! Contact '{name}' saved.")
    except Exception as e:
        # Show any insert error.
        print(f"Error: {e}")
    finally:
        # Always close the connection.
        conn.close()


# Add a new phone number to an existing contact.
def add_phone():
    # Ask for the contact name.
    name  = input("Existing contact name: ")
    # Ask for the phone number.
    phone = input("Phone number: ")
    # Show the type options to the user.
    print("Type:  1=mobile  2=home  3=work")
    # Default the type to mobile.
    t = input("Choose [1]: ") or "1"
    # Translate menu choice to database value.
    types = {"1": "mobile", "2": "home", "3": "work"}
    # Pick the correct phone type.
    phone_type = types.get(t, "mobile")

    # Open the DB connection.
    conn = get_connection()
    # Stop if connection is unavailable.
    if not conn: return
    try:
        # Call the stored procedure in the database.
        with conn, conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        # Confirm success to the user.
        print("Done! Phone added.")
    except Exception as e:
        # Show the error if the procedure fails.
        print(f"Error: {e}")
    finally:
        # Always close the connection.
        conn.close()


# Move a contact into a new or existing group.
def move_to_group():
    # Ask for the contact name.
    name       = input("Contact name: ")
    # Ask for the destination group.
    group_name = input("Group name (Family / Work / Friend / Other): ")

    # Open the DB connection.
    conn = get_connection()
    # Stop if connection is unavailable.
    if not conn: return
    try:
        # Call the database procedure that moves the contact.
        with conn, conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        # Confirm success.
        print(f"Done! '{name}' moved to group '{group_name}'.")
    except Exception as e:
        # Show any error.
        print(f"Error: {e}")
    finally:
        # Close the connection.
        conn.close()


# Import contacts from a CSV file.
def import_csv():
    # Ask for the file path, but default to the project CSV.
    filepath = input(f"CSV file path [{BASE_DIR / 'contacts.csv'}]: ").strip() or str(BASE_DIR / "contacts.csv")
    # Make sure the file exists.
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # Count how many records are inserted.
    inserted = 0
    # Count how many rows were skipped.
    skipped  = 0

    # Open the DB connection.
    conn = get_connection()
    # Stop if connection is unavailable.
    if not conn: return
    try:
        # Use a cursor for all insert operations.
        with conn, conn.cursor() as cur:
            # Open the CSV file with UTF-8 encoding.
            with open(filepath, newline="", encoding="utf-8") as f:
                # Read rows by column name.
                reader = csv.DictReader(f)
                # Process one CSV row at a time.
                for row in reader:
                    # Get and clean the contact name.
                    name = row.get("name", "").strip()
                    # Skip rows without a name.
                    if not name:
                        skipped += 1
                        continue

                    # Check whether this contact already exists.
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                    # If a row already exists, skip it.
                    if cur.fetchone():
                        print(f"  Skip (already exists): {name}")
                        skipped += 1
                        continue

                    # Create or find the group for this contact.
                    group_id = get_group_id(cur, row.get("group", "").strip())
                    # Read birthday from the CSV if present.
                    birthday = row.get("birthday", "").strip() or None
                    # Read email from the CSV if present.
                    email    = row.get("email",    "").strip() or None

                    # Insert the contact row into the contacts table.
                    cur.execute(
                        "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
                        (name, email, birthday, group_id)
                    )
                    # Get the new contact ID.
                    cid = cur.fetchone()[0]

                    # Read the first phone number.
                    phone_val  = row.get("phone", "").strip()
                    # Read the phone type, defaulting to mobile.
                    phone_type = row.get("type",  "mobile").strip() or "mobile"
                    # Only insert a phone if one was supplied.
                    if phone_val:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, phone_val, phone_type)
                        )
                    # Count this row as inserted.
                    inserted += 1

        # Save all imported rows.
        conn.commit()
        # Show import summary.
        print(f"\nDone! Inserted: {inserted}, Skipped: {skipped}")
    except Exception as e:
        # Show the error if import fails.
        print(f"Error: {e}")
    finally:
        # Close the connection.
        conn.close()


# Import contacts from a JSON file.
def import_json():
    # Ask for the JSON file path, with a sensible default.
    filepath = input(f"JSON file path [{BASE_DIR / 'contacts_export.json'}]: ").strip() or str(BASE_DIR / "contacts_export.json")
    # Stop if the file is missing.
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # Read the JSON file into Python data.
    with open(filepath, encoding="utf-8") as f:
        records = json.load(f)

    # Count inserted contacts.
    inserted = 0
    # Count skipped contacts.
    skipped  = 0
    # Count overwritten contacts.
    updated  = 0

    # Open the DB connection.
    conn = get_connection()
    # Stop if connection is unavailable.
    if not conn: return
    try:
        # Use one cursor for the whole import.
        with conn, conn.cursor() as cur:
            # Process each JSON record one by one.
            for rec in records:
                # Clean up the contact name.
                name = rec.get("name", "").strip()
                # Skip empty names.
                if not name:
                    skipped += 1
                    continue

                # Check if this name already exists in the DB.
                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                # Read the existing contact if one was found.
                existing = cur.fetchone()

                # If the contact exists, ask what to do.
                if existing:
                    print(f"\nDuplicate found: '{name}'")
                    # Ask the user to skip or overwrite.
                    action = input("  [s]kip or [o]verwrite? ").lower()
                    # Anything except "o" means skip.
                    if action != "o":
                        skipped += 1
                        continue

                    # Keep the existing contact ID.
                    cid      = existing[0]
                    # Make sure the group exists.
                    group_id = get_group_id(cur, rec.get("group"))
                    # Update the contact's main fields.
                    cur.execute(
                        "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                        (rec.get("email"), rec.get("birthday"), group_id, cid)
                    )
                    # Remove old phones before inserting the new list.
                    cur.execute("DELETE FROM phones WHERE contact_id = %s", (cid,))
                    # Count this record as updated.
                    updated += 1
                else:
                    # Create or find the group for this new contact.
                    group_id = get_group_id(cur, rec.get("group"))
                    # Insert the new contact row.
                    cur.execute(
                        "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
                        (name, rec.get("email"), rec.get("birthday"), group_id)
                    )
                    # Save the newly created contact ID.
                    cid = cur.fetchone()[0]
                    # Count this record as inserted.
                    inserted += 1

                # Add each phone entry from the JSON record.
                for ph in rec.get("phones", []):
                    # Clean phone value.
                    p_val  = ph.get("phone", "").strip()
                    # Read phone type, defaulting to mobile.
                    p_type = ph.get("type", "mobile")
                    # Only insert non-empty phone numbers.
                    if p_val:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, p_val, p_type)
                        )

        # Commit all JSON import changes.
        conn.commit()
        # Show the summary of what happened.
        print(f"\nDone! Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}")
    except Exception as e:
        # Show the error if something goes wrong.
        print(f"Error: {e}")
    finally:
        # Close the DB connection.
        conn.close()


# Export every contact to a JSON file.
def export_json():
    # Ask where to save the file, with a default path.
    filepath = input(f"Save as [{BASE_DIR / 'contacts_export.json'}]: ").strip() or str(BASE_DIR / "contacts_export.json")

    # Open the DB connection.
    conn = get_connection()
    # Stop if connection is unavailable.
    if not conn: return
    try:
        # This will hold the exported rows.
        records = []
        # Use a cursor to fetch contacts and phones.
        with conn, conn.cursor() as cur:
            # Get all contacts.
            cur.execute("SELECT id, name, email, birthday, group_id FROM contacts ORDER BY name")
            # Read the contact list.
            contacts = cur.fetchall()

            # Process each contact one by one.
            for cid, name, email, birthday, group_id in contacts:
                # Default group name to None.
                group_name = None
                # Look up the group name if the contact has a group.
                if group_id:
                    cur.execute("SELECT name FROM groups WHERE id = %s", (group_id,))
                    # Read the group row.
                    g = cur.fetchone()
                    # Save the group name if found.
                    group_name = g[0] if g else None

                # Load all phone numbers for this contact.
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY type",
                    (cid,)
                )
                # Turn the rows into JSON-friendly dictionaries.
                phones = [{"phone": r[0], "type": r[1]} for r in cur.fetchall()]

                # Build one export object for this contact.
                records.append({
                    "name":     name,
                    "email":    email,
                    "birthday": birthday.isoformat() if birthday else None,
                    "group":    group_name,
                    "phones":   phones
                })

        # Write all records to the target file.
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        # Confirm success.
        print(f"Done! {len(records)} contacts exported to '{filepath}'.")
    except Exception as e:
        # Show any export error.
        print(f"Error: {e}")
    finally:
        # Close the DB connection.
        conn.close()


# Display the main menu and route the user's choice.
def main():
    # Show the title.
    print("\n=== PhoneBook TSIS 1 ===")
    # Tell the user how to initialize the database.
    print("First time? Choose 0 to set up the database.\n")

    # Keep running until the user exits.
    while True:
        # Print the menu sections and actions.
        print("--- MENU ---")
        print("0.  Setup database (run once)")
        print("--- Search & Filter ---")
        print("1.  Search by name / email / phone")
        print("2.  Filter by group")
        print("3.  Search by email")
        print("4.  Show all contacts (sorted)")
        print("5.  Browse page by page")
        print("--- Phone & Group ---")
        print("6.  Add new contact")
        print("7.  Add phone to existing contact")
        print("8.  Move contact to group")
        print("--- Import / Export ---")
        print("9.  Import from CSV")
        print("10. Import from JSON")
        print("11. Export to JSON")
        print("12. Exit")

        # Read the menu choice from the user.
        choice = input("\nChoose: ").strip()

        # Dispatch the chosen action.
        if   choice == "0":  setup_database()
        elif choice == "1":  search_all()
        elif choice == "2":  filter_by_group()
        elif choice == "3":  search_by_email()
        elif choice == "4":  show_sorted()
        elif choice == "5":  browse_pages()
        elif choice == "6":  add_contact()
        elif choice == "7":  add_phone()
        elif choice == "8":  move_to_group()
        elif choice == "9":  import_csv()
        elif choice == "10": import_json()
        elif choice == "11": export_json()
        elif choice == "12":
            # Leave the program.
            print("Goodbye!")
            break
        else:
            # Handle invalid menu input.
            print("Wrong choice, try again.")


if __name__ == '__main__':
    # Run the menu only when this file is executed directly.
    main()

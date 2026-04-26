# TSIS 1 - Phonebook

This project is a PostgreSQL-based phonebook app with stored procedures and import/export helpers.

## Requirements

- PostgreSQL running locally
- Python package: `psycopg2-binary`

Install dependencies with:

```bash
pip install -r TSIS/TSIS1/requirements.txt
```

## Run

```bash
python3 TSIS/TSIS1/phonebook.py
```

## First-time setup

1. Make sure the database settings in `config.py` match your local PostgreSQL user.
2. Run the app and choose `0` to create the tables and load `procedures.sql`.

## Features

- Search contacts by name, email, or phone
- Filter contacts by group
- Add phones and move contacts between groups
- Import from CSV and JSON
- Export contacts to JSON

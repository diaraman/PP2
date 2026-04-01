import psycopg2
from config import DB_CONFIG

def get_connection():
    # Practice 8 helper: single place for creating a DB connection.
    return psycopg2.connect(**DB_CONFIG)

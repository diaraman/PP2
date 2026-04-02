import psycopg2
from config import DB_CONFIG

def get_connection():
    # Single place for creating a DB connection.
    return psycopg2.connect(**DB_CONFIG)

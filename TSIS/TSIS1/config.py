def load_config():
    # This function keeps the connection settings in one place.
    # If the database changes later, you only edit this one dictionary.
    return {
        "host":     "localhost",
        "database": "phonebook_db",
        "user":     "postgres",
        "password": "1234"        # <- поменяй на свой пароль
    }

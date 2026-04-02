-- Practice 8: PostgreSQL functions for PhoneBook.
-- Functions are called with SELECT and return data.

-- Scalar-returning function (RETURNS INT)
CREATE OR REPLACE FUNCTION phonebook_total_count()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_total INT;
BEGIN
    -- Count all rows in the main phonebook table.
    SELECT COUNT(*) INTO v_total
    FROM phonebook_users;

    RETURN v_total;
END;
$$;

-- Returns table: find contacts by pattern in name, surname, username, or phone
CREATE OR REPLACE FUNCTION phonebook_search(p_pattern TEXT)
RETURNS TABLE (
    id INT,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- RETURN QUERY sends a result set back from a function.
    RETURN QUERY
    SELECT
        u.id,
        u.username,
        u.first_name,
        u.last_name,
        u.phone
    FROM phonebook_users AS u
    WHERE u.first_name ILIKE '%' || p_pattern || '%'
       OR u.last_name ILIKE '%' || p_pattern || '%'
       OR u.username ILIKE '%' || p_pattern || '%' 
       OR u.phone ILIKE '%' || p_pattern || '%'
    ORDER BY u.id;
END;
$$;

-- Returns table with pagination (LIMIT/OFFSET)
CREATE OR REPLACE FUNCTION phonebook_get_page(
    p_limit INT DEFAULT 10,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    id INT,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Defensive checks so pagination inputs are valid.
    IF p_limit <= 0 THEN
        RAISE EXCEPTION 'p_limit must be greater than 0';
    END IF;

    IF p_offset < 0 THEN
        RAISE EXCEPTION 'p_offset must be >= 0';
    END IF;

    RETURN QUERY
    SELECT
        u.id,
        u.username,
        u.first_name,
        u.last_name,
        u.phone
    FROM phonebook_users AS u
    ORDER BY u.id
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;

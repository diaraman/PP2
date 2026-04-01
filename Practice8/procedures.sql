-- Practice 8: PostgreSQL stored procedures for PhoneBook (upsert/bulk/delete).
-- Procedures are called with CALL and mainly perform actions (insert/update/delete).

-- Upsert one user by name + phone.
-- If user exists (same username), phone is updated.
CREATE OR REPLACE PROCEDURE phonebook_upsert_user(
    p_name TEXT,
    p_phone TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_name TEXT;
    v_username TEXT;
BEGIN
    v_name := BTRIM(COALESCE(p_name, ''));

    -- Validate required values before writing to table.
    IF v_name = '' THEN
        RAISE EXCEPTION 'Name cannot be empty';
    END IF;

    IF p_phone IS NULL OR p_phone !~ '^\+?[0-9]{10,15}$' THEN
        RAISE EXCEPTION 'Invalid phone format: %', p_phone;
    END IF;

    v_username := LOWER(REPLACE(v_name, ' ', '_'));

    BEGIN
        -- Upsert by username: insert new user or update existing user.
        INSERT INTO phonebook_users (username, first_name, last_name, phone)
        VALUES (
            v_username,
            split_part(v_name, ' ', 1),
            CASE
                WHEN position(' ' IN v_name) > 0
                    THEN NULLIF(BTRIM(substring(v_name FROM position(' ' IN v_name) + 1)), '')
                ELSE NULL
            END,
            p_phone
        )
        ON CONFLICT (username)
        DO UPDATE SET
            phone = EXCLUDED.phone,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name;
    EXCEPTION
        WHEN unique_violation THEN
            RAISE EXCEPTION 'Phone already belongs to another user: %', p_phone;
    END;
END;
$$;

-- Bulk insert/update from arrays of names and phones.
-- Uses FOR and IF, validates phone format, and returns all invalid records via INOUT jsonb.
CREATE OR REPLACE PROCEDURE phonebook_bulk_upsert_users(
    p_names TEXT[],
    p_phones TEXT[],
    INOUT p_invalid JSONB DEFAULT '[]'::JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_name TEXT;
    v_phone TEXT;
BEGIN
    IF COALESCE(array_length(p_names, 1), 0) = 0 THEN
        RETURN;
    END IF;

    FOR i IN 1..array_length(p_names, 1) LOOP
        -- Read the i-th input pair and normalize spacing.
        v_name := BTRIM(COALESCE(p_names[i], ''));
        v_phone := CASE
            WHEN i <= COALESCE(array_length(p_phones, 1), 0) THEN BTRIM(COALESCE(p_phones[i], ''))
            ELSE ''
        END;

        IF v_name = '' THEN
            -- Collect bad rows instead of failing the whole batch.
            p_invalid := p_invalid || jsonb_build_array(
                jsonb_build_object(
                    'index', i,
                    'name', p_names[i],
                    'phone', v_phone,
                    'reason', 'empty_name'
                )
            );
        ELSIF v_phone !~ '^\+?[0-9]{10,15}$' THEN
            p_invalid := p_invalid || jsonb_build_array(
                jsonb_build_object(
                    'index', i,
                    'name', p_names[i],
                    'phone', v_phone,
                    'reason', 'invalid_phone'
                )
            );
        ELSE
            BEGIN
                -- Reuse single-row procedure for consistent rules.
                CALL phonebook_upsert_user(v_name, v_phone);
            EXCEPTION
                WHEN OTHERS THEN
                    -- Save database error text per row for debugging/reporting.
                    p_invalid := p_invalid || jsonb_build_array(
                        jsonb_build_object(
                            'index', i,
                            'name', p_names[i],
                            'phone', v_phone,
                            'reason', SQLERRM
                        )
                    );
            END;
        END IF;
    END LOOP;
END;
$$;

-- Delete by username or by phone
CREATE OR REPLACE PROCEDURE phonebook_delete_user(
    p_username TEXT DEFAULT NULL,
    p_phone TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- At least one delete criterion must be provided.
    IF p_username IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'Provide p_username or p_phone';
    END IF;

    DELETE FROM phonebook_users
    WHERE (p_username IS NOT NULL AND username = p_username)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;

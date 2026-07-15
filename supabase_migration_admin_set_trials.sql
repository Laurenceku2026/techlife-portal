-- Run in the SAME Supabase project: wglfpwlqesjrxonfaaeb
-- Replace YOUR_APP_SCHEMA below with the portal/DFSS schema (NOT public, if you use schema isolation).
-- Also expose that schema in: Project Settings → API → Exposed schemas.

-- Example: if portal tables live in schema "dfss", replace YOUR_APP_SCHEMA with dfss.

CREATE OR REPLACE FUNCTION YOUR_APP_SCHEMA.admin_set_free_trials(
    p_email text,
    p_trials integer,
    p_app_id text DEFAULT NULL
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = YOUR_APP_SCHEMA, public
AS $$
DECLARE
    updated_count integer := 0;
BEGIN
    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RETURN 0;
    END IF;

    IF p_app_id IS NULL OR btrim(p_app_id) = '' THEN
        UPDATE YOUR_APP_SCHEMA.profiles
        SET free_trials_remaining = COALESCE(p_trials, 0)
        WHERE lower(email) = lower(btrim(p_email));
    ELSE
        UPDATE YOUR_APP_SCHEMA.profiles
        SET free_trials_remaining = COALESCE(p_trials, 0)
        WHERE lower(email) = lower(btrim(p_email))
          AND app_id::text = btrim(p_app_id);
    END IF;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$;

REVOKE ALL ON FUNCTION YOUR_APP_SCHEMA.admin_set_free_trials(text, integer, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION YOUR_APP_SCHEMA.admin_set_free_trials(text, integer, text) TO service_role;

-- Admin helper: set free trials by email (bypasses some client RLS pitfalls)
-- Run once in Supabase SQL Editor, then retry "重置次数为 30" in the portal admin.

CREATE OR REPLACE FUNCTION public.admin_set_free_trials(p_email text, p_trials integer)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    updated_count integer := 0;
BEGIN
    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RETURN 0;
    END IF;

    UPDATE public.profiles
    SET free_trials_remaining = COALESCE(p_trials, 0)
    WHERE lower(email) = lower(btrim(p_email));

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$;

REVOKE ALL ON FUNCTION public.admin_set_free_trials(text, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.admin_set_free_trials(text, integer) TO service_role;

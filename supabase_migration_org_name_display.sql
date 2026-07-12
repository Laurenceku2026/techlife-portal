-- Organization name display mode: auto (follow UI language), zh, or en
-- Run once in Supabase SQL Editor (Dashboard → SQL → New query)

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS name_display_mode TEXT NOT NULL DEFAULT 'auto';

ALTER TABLE organizations
    DROP CONSTRAINT IF EXISTS organizations_name_display_mode_check;

ALTER TABLE organizations
    ADD CONSTRAINT organizations_name_display_mode_check
    CHECK (name_display_mode IN ('auto', 'zh', 'en'));

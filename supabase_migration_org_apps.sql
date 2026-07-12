-- Per-organization enabled child apps (platform admin configurable)
-- Run once in Supabase SQL Editor after supabase_migration_enterprise.sql

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS enabled_apps JSONB;

UPDATE organizations
SET enabled_apps = '["feasibility","dqa","fa","paravary","eml"]'::jsonb
WHERE enabled_apps IS NULL;

ALTER TABLE organizations
    ALTER COLUMN enabled_apps SET DEFAULT '["feasibility","dqa","fa","paravary","eml"]'::jsonb;

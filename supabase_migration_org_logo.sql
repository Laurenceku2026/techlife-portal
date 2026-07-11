-- Add organization logo storage (data URL or public URL in logo_url column)
-- Run once in Supabase SQL Editor after supabase_migration_enterprise.sql

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS logo_url TEXT;

-- Bilingual organization names (Chinese / English)
-- Run once in Supabase SQL Editor (Dashboard → SQL → New query)

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS name_zh TEXT,
    ADD COLUMN IF NOT EXISTS name_en TEXT;

-- Backfill Chinese name from legacy single name column
UPDATE organizations
SET name_zh = name
WHERE (name_zh IS NULL OR btrim(name_zh) = '')
  AND name IS NOT NULL
  AND btrim(name) <> '';

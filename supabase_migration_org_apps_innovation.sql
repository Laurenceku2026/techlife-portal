-- Add Innovation Assessment to organization app catalogs.
-- Run once in Supabase SQL Editor.

ALTER TABLE organizations
    ALTER COLUMN enabled_apps SET DEFAULT
    '["innovation","feasibility","dqa","fa","paravary","eml"]'::jsonb;

UPDATE organizations
SET enabled_apps = '["innovation","feasibility","dqa","fa","paravary","eml"]'::jsonb
WHERE enabled_apps IS NULL
   OR enabled_apps = '["feasibility","dqa","fa","paravary","eml"]'::jsonb;

-- Orgs that already include Product Feasibility but not Innovation Assessment.
UPDATE organizations
SET enabled_apps = '["innovation"]'::jsonb || enabled_apps
WHERE enabled_apps IS NOT NULL
  AND enabled_apps ? 'feasibility'
  AND NOT (enabled_apps ? 'innovation');

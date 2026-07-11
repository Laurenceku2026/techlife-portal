-- TechLife Portal enterprise multi-tenant schema
-- Run once in Supabase SQL Editor (Dashboard → SQL → New query)

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    max_seats INTEGER NOT NULL DEFAULT 10,
    is_active BOOLEAN NOT NULL DEFAULT true,
    contract_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE profiles
    ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL;

ALTER TABLE profiles
    ADD COLUMN IF NOT EXISTS org_role TEXT CHECK (org_role IS NULL OR org_role IN ('admin', 'member'));

ALTER TABLE knowledge_base
    ADD COLUMN IF NOT EXISTS scope TEXT NOT NULL DEFAULT 'platform';

ALTER TABLE knowledge_base
    ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Backfill existing rows as platform-wide knowledge
UPDATE knowledge_base SET scope = 'platform' WHERE scope IS NULL;

CREATE INDEX IF NOT EXISTS idx_profiles_organization_id ON profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_tenant ON knowledge_base(organization_id)
    WHERE scope = 'tenant';

CREATE SCHEMA selfemployed_fns_receipts;


CREATE TABLE selfemployed_fns_receipts.transactions(
    id BIGINT PRIMARY KEY,
    park_id TEXT NOT NULL,
    contractor_profile_id TEXT NOT NULL,
    business_unit TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_id BIGINT NOT NULL,
    income NUMERIC NOT NULL,
    legal_entity TEXT,
    event_at TIMESTAMPTZ NOT NULL,
    state TEXT NOT NULL DEFAULT 'created',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_updated_at
BEFORE UPDATE ON selfemployed_fns_receipts.transactions
FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

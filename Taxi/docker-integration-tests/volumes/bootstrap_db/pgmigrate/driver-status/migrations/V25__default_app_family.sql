-- Intermediate migration for TAXIDRIVERORDER-355
-- Temporary set default value 1 (taximeter) for ds.drivers.app_family_id
-- Column ds.drivers.app_family_id should be dropped in the next migration
ALTER TABLE ds.drivers
ALTER COLUMN app_family_id
SET DEFAULT 1;

DROP TRIGGER IF EXISTS set_updated_at_timestamp_places
    ON storage.places;

BEGIN;
-- В проде база зон занята и таймаута 1s не хватает
SET LOCAL lock_timeout='3s';
DROP TRIGGER IF EXISTS set_updated_at_timestamp_delivery_zones
    ON storage.delivery_zones;
COMMIT;

DROP FUNCTION trigger_set_updated_at_timestamp;

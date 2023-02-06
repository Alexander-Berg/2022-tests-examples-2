BEGIN;
-- В проде в таблицу зон идут 15 RPS на запись и таймаута 1s не хватает:
SET LOCAL lock_timeout='3s';

CREATE SEQUENCE storage.delivery_zones_id_seq
    START 5000000
    OWNED BY storage.delivery_zones.id;

ALTER TABLE storage.delivery_zones
    ALTER COLUMN id SET DEFAULT nextval('storage.delivery_zones_id_seq');

COMMIT;

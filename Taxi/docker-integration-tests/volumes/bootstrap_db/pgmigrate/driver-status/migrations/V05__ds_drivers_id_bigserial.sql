ALTER TABLE ds.drivers
    ALTER COLUMN id TYPE BIGINT;

ALTER TABLE ds.blocks
    ALTER COLUMN driver_id TYPE BIGINT;

ALTER TABLE ds.modifiers
    ALTER COLUMN driver_id TYPE BIGINT;

ALTER TABLE ds.orders
    ALTER COLUMN driver_id TYPE BIGINT;

ALTER TABLE ds.statuses
    ALTER COLUMN driver_id TYPE BIGINT;

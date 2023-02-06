START TRANSACTION;

CREATE TABLE eats_ordershistory.addresses(
    order_id TEXT NOT NULL PRIMARY KEY,
    full_address TEXT,
    entrance TEXT,
    floor_number TEXT,
    office TEXT,
    doorcode TEXT,
    comment TEXT
);

CREATE TYPE eats_ordershistory.address_v1 AS (
    order_id TEXT,
    full_address TEXT,
    entrance TEXT,
    floor_number TEXT,
    office TEXT,
    doorcode TEXT,
    comment TEXT
);

COMMIT;

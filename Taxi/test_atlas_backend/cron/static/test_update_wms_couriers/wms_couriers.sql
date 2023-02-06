CREATE TABLE IF NOT EXISTS "taxi_db_postgres_atlas_backend"."wms_couriers"
(
    courier_id TEXT PRIMARY KEY,
    courier_external_id TEXT,
    name TEXT,
    source TEXT,
    status TEXT,
    free_time NUMERIC,
    shift_type TEXT,
    updated_at TIMESTAMP NOT NULL
);

INSERT INTO "taxi_db_postgres_atlas_backend"."wms_couriers"
    VALUES ('6f087c7c54154702a9a569b89a53cb10000200020000',
            '1f01b6133ef847229380315bcaa7a7ec_48653acd8bc5b173b8e52eb02c976fd8',
            'Lavka Courier', 'lavka', 'free', 1548.0, 'plan', '2022-03-31 12:00:00');

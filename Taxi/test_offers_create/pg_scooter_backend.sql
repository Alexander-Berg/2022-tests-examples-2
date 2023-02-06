-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/drive_offers
CREATE TABLE IF NOT EXISTS drive_offers (
    id text PRIMARY KEY,
    constructor_id text NOT NULL,
    object_id uuid NOT NULL,
    user_id uuid NOT NULL,
    deadline bigint NOT NULL,
    data text NOT NULL
);

TRUNCATE drive_offers;

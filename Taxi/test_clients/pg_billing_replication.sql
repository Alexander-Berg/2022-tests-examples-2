INSERT INTO corp.clients (
    id,
    corp_id,
    yandex_uid,
    created,
    updated,
    updated_at_timestamp,
    updated_at_ordinal
) VALUES
    ('client_id1_billing_id', 'client_id1', 'yandex_uid1', clock_timestamp(), clock_timestamp(), 0, 0);


INSERT INTO parks.clients (
    id,
    park_id,
    created,
    updated
) VALUES
    ('client_id2', 'park_id2', clock_timestamp(), clock_timestamp());

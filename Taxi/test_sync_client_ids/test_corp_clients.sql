INSERT INTO corp.clients(
    id,
    corp_id,
    yandex_uid,
    created,
    updated,
    updated_at_timestamp,
    updated_at_ordinal
)
VALUES
    (1, 'client_id1', 'client_id1_uid', clock_timestamp(), (clock_timestamp() at time zone 'utc')::timestamp - interval '1 hour', 0, 0),
    (2, 'client_id2', 'client_id2_uid', clock_timestamp(), (clock_timestamp() at time zone 'utc')::timestamp - interval '1 hour', 0, 0),
    (3, 'client_id3', 'client_id3_uid', clock_timestamp(), (clock_timestamp() at time zone 'utc')::timestamp - interval '1 hour', 0, 0);

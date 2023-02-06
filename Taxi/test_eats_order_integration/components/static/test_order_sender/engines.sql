INSERT INTO integration_engines
(
    id,
    name,
    engine_class
)
values
(
    1,
    'test1',
    null
),
(
    2,
    'test2',
    null
)
;

INSERT INTO partner_engine_settings(
    place_group_id,
    engine_id,
    credentials,
    settings
)
VALUES
(
    'place_group_id_1',
    1,
    '{"client_id": "MTjH8+43BcRUKDjdPp1UUuPc4Vmk+I6TSrwptL6+6ZM=", "client_secret": "j+aDrVnrQJdlCBKa38N2UxO4prB0s4N7V399j8fuMo4PnqeruldFKzLAowNvipRi", "vendor_host": "$mockserver/eats-partner-engine-yandex-eda", "scope": "read write", "dek": "qn+Sg4d1uMLTkaOpib8i4FcD1xxJEdIQyMjIyelTWiAhZV0YSZWkA1xZ3w7FtCI/Ar9rU08OgdmBlhtDudowkQ=="}',
    '{}'
)
;
INSERT INTO order_flow
(
    idempotency_key,
    is_locked,
    order_nr,
    status
)
values
(
    'idempotency_key',
    true,
    'order_id',
    'NEW'
),
(
    'idempotency_key_sent_to_partner',
    true,
    'order_id',
    'SENT_TO_PARTNER'
)
;

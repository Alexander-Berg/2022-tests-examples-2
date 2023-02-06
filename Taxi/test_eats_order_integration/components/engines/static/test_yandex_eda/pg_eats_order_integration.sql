INSERT INTO integration_engines
(
    id,
    name,
    engine_class
)
values
(
    114,
    'Yandex.Eda API',
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
    114,
    '{"client_id": "MTjH8+43BcRUKDjdPp1UUuPc4Vmk+I6TSrwptL6+6ZM=", "client_secret": "j+aDrVnrQJdlCBKa38N2UxO4prB0s4N7V399j8fuMo4PnqeruldFKzLAowNvipRi", "vendor_host": "$mockserver/eats-partner-engine-yandex-eda", "scope": "read write", "dek": "qn+Sg4d1uMLTkaOpib8i4FcD1xxJEdIQyMjIyelTWiAhZV0YSZWkA1xZ3w7FtCI/Ar9rU08OgdmBlhtDudowkQ=="}',
    '{}'
),
(
    'place_group_id_2',
    114,
    '{"client_id": "MTjH8+43BcRUKDjdPp1UUuPc4Vmk+I6TSrwptL6+6ZM=", "client_secret": "j+aDrVnrQJdlCBKa38N2UxO4prB0s4N7V399j8fuMo4PnqeruldFKzLAowNvipRi", "vendor_host": "$mockserver/eats-partner-engine-yandex-eda", "scope": "read write", "dek": "qn+Sg4d1uMLTkaOpib8i4FcD1xxJEdIQyMjIyelTWiAhZV0YSZWkA1xZ3w7FtCI/Ar9rU08OgdmBlhtDudowkQ=="}',
    '{"resendOrder": false}'
)
;

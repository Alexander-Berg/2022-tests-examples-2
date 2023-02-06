INSERT INTO integration_engines
(
    id,
    name,
    engine_class,
    is_hidden
)
values
(
    1,
    'test1',
    null,
    false
),
(
    2,
    'test2',
    null,
    false
)
;

INSERT INTO partner_engine_settings(
    place_group_id,
    engine_id,
    credentials
)
VALUES
(
    'place_group_id_1',
    1,
    '{"client_id": "MTjH8+43BcRUKDjdPp1UUuPc4Vmk+I6TSrwptL6+6ZM=", "client_secret": "j+aDrVnrQJdlCBKa38N2UxO4prB0s4N7V399j8fuMo4PnqeruldFKzLAowNvipRi", "vendor_host": "http://localhost:8080/v1/", "scope": "read write", "dek": "qn+Sg4d1uMLTkaOpib8i4FcD1xxJEdIQyMjIyelTWiAhZV0YSZWkA1xZ3w7FtCI/Ar9rU08OgdmBlhtDudowkQ=="}'
)
;

INSERT INTO places(
    place_id,
    place_group_id,
    brand_id,
    brand_name
)
VALUES
(
    'place1',
    'place_group_id_1',
    'brand1',
    'name1'
)
;

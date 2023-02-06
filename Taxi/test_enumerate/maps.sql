/* V2 */
INSERT INTO maps.maps
       (content_key, type, map, created_time, compression)
VALUES
       ('taxi_surge/__default__',
        'some_type',
        'some_binary_\000_data'::BYTEA,
        '2019-01-02 00:00:00'::TIMESTAMP,
        'none'),
       ('taxi_surge/__default__',
        'some_type',
        'some_binary_\000_data'::BYTEA,
        '2019-01-01 00:00:00'::TIMESTAMP,
        'none'),
       ('taxi_surge/uberX',
        'some_type',
        'some_binary_\000_data'::BYTEA,
        '2019-01-02 00:00:00'::TIMESTAMP,
        'none'),
       ('eda_surge/mcDuck',
        'some_type',
        'some_binary_\000_data'::BYTEA,
        '2019-01-02 00:00:00'::TIMESTAMP,
        'none');

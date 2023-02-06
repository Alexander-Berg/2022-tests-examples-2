/* V2 */
INSERT INTO maps.maps
       (content_key, type, map, created_time, compression)
VALUES
       ('some_content',
        'some_type',
        'some_binary_\000_data'::BYTEA,
        '2019-01-02 00:00:00'::TIMESTAMP,
        'none');

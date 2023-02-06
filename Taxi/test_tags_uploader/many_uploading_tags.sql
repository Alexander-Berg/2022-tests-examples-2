INSERT INTO state.uploading_tags (
    tags_id,
    driver_id_id,
    udid,
    merge_policy,
    confirmation_token,
    tags,
    ttl,
    uploaded,
    provider,
    created_at
)
VALUES
    (
        1000,
        IdId('uuid3', 'dbid777'),
        '000000000000000000000011',
        'remove',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1001,
        IdId('uuid3', 'dbid777'),
        '000000000000000000000011',
        'remove',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1002,
        IdId('uuid3', 'dbid777'),
        '000000000000000000000011',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1003,
        IdId('uuid2', 'dbidparis'),
        '000000000000000000000012',
        'remove',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1004,
        IdId('uuid2', 'dbidparis'),
        '000000000000000000000012',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1005,
        IdId('uuid2', 'dbidparis'),
        '000000000000000000000012',
        'remove',
        'error_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1006,
        IdId('driverSS', '1488'),
        '000000000000000000000013',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1007,
        IdId('driverSS', '1488'),
        '000000000000000000000013',
        'remove',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1008,
        IdId('driverSS', '1488'),
        '000000000000000000000013',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1009,
        IdId('pg_driver', 'pg_park'),
        '000000000000000000000014',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T12:00:03',
        False,
        ('reposition')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1010,
        IdId('uuid3', 'dbid777'),
        '000000000000000000000011',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition-relocator')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1011,
        IdId('uuid3', 'dbid777'),
        '000000000000000000000011',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition-relocator')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1012,
        IdId('uuid2', 'dbidparis'),
        '000000000000000000000012',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition-relocator')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1013,
        IdId('uuid2', 'dbidparis'),
        '000000000000000000000012',
        'remove',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition-relocator')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1014,
        IdId('driverSS', '1488'),
        '000000000000000000000013',
        'remove',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition-relocator')::db.tags_provider,
        '2019-09-01T12:00:00'
    ),
    (
        1015,
        IdId('driverSS', '1488'),
        '000000000000000000000013',
        'append',
        'any_token',
        '{"tag_0", "tag_1"}',
        '2019-09-01T13:00:00',
        False,
        ('reposition-relocator')::db.tags_provider,
        '2019-09-01T12:00:00'
    )
;
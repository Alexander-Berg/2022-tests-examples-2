INSERT INTO state.uploading_tags (
    tags_id,
    udid,
    driver_id_id,
    merge_policy,
    confirmation_token,
    tags,
    ttl,
    uploading,
    uploaded,
    provider,
    created_at
)
VALUES
(
    1000,
    '000000000000000000000011',
    IdId('uuid', 'dbid777'),
    'append',
    'any_token',
    '{"tag_0", "tag_1"}',
    '2019-09-01T13:30:00',
    '2019-09-01T12:59:30',
    True,
    ('reposition')::db.tags_provider,
    '2019-09-01T12:30:00'
),
(
    1500,
    '000000000000000000000011',
    IdId('uuid', 'dbid777'),
    'append',
    'any_token',
    '{"tag_3"}',
    '2019-09-01T13:30:00',
    '2019-09-01T12:59:30',
    True,
    ('reposition')::db.tags_provider,
    '2019-09-01T12:30:00'
),
(
    2000,
    '000000000000000000000011',
    IdId('uuid', 'dbid777'),
    'remove',
    'any_token',
    '{"tag_1"}',
    '2019-09-01T13:30:00',
    '2019-09-01T12:59:30',
    True,
    ('reposition')::db.tags_provider,
    '2019-09-01T12:30:00'
),
(
    3000,
    '000000000000000000000011',
    IdId('uuid', 'dbid777'),
    'append',
    'any_token',
    '{"tag_2"}',
    '2019-09-01T13:30:00',
    '2019-09-01T12:59:30',
    True,
    ('reposition-relocator')::db.tags_provider,
    '2019-09-01T12:30:00'
);

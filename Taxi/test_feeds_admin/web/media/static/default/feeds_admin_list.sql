INSERT INTO feeds_admin.media
(
    media_id,
    media_type,
    storage_type,
    storage_settings,
    service_group,
    tags,
    created,
    updated
)
VALUES
    (
        'image',
        'image',
        'avatars',
        '{"group-id": 1396527, "sizes": {"foo": "bar"}}'::jsonb,
        'test_group',
        ARRAY['some_tag'],
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '4001-01-01 00:00:00+0300'::timestamp with time zone
    ),
    (
        'image2',
        'image',
        'avatars',
        '{"group-id": 1396527, "sizes": {"foo": "bar"}}'::jsonb,
        'test_group',
        ARRAY['another_tag'],
        '2500-01-01 00:00:00+0300'::timestamp with time zone,
        '3501-01-01 00:00:00+0300'::timestamp with time zone
    ),
    (
        'video',
        'video',
        's3',
        '{
          "service": "example",
          "bucket_name": "feeds-admin-bucket"
        }'::jsonb,
        'test_group',
        ARRAY['another_tag'],
        '3000-01-02 00:00:00+0300'::timestamp with time zone,
        '3000-01-02 00:00:00+0300'::timestamp with time zone
    )

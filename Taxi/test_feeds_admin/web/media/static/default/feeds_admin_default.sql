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
        'existed_image',
        'image',
        'avatars',
        '{"group-id": 1396527, "sizes": {"foo": "bar"}}'::jsonb,
        'test_group',
        ARRAY[]::text[],
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone
    )

INSERT INTO corp_announcements.images (
    image_id,
    name,
    avatars_group_id,
    sizes,
    created_at,
    created_by
)
VALUES (
    'image_id_001',
    'kitten0.jpg',
    123,
    '{"orig": {"width": 123, "height": 456}}',
    '2019-08-18 15:30:27'::timestamp,
    10000000000
),
(
    'image_id_002',
    'kitten0.jpg',
    123,
    '{"orig": {"width": 123, "height": 456}}',
    '2019-08-18 15:30:27'::timestamp,
    20000000000
);


INSERT INTO restaurants (
    place_id,
    slug,
    name,
    pos_type,
    created_at,
    billing_client_id,
    personal_tin_id
)
VALUES
(
    '1',
    'place_id__1_slug',
    'Ресторан "Рыба 1"',
    'rkeeper',
    '2022-06-14 00:00:00Z',
    NULL,
    'personal_tin_id__1'
),
(
    '2',
    'place_id__2_slug',
    'Ресторан "Рыба 2"',
    'rkeeper',
    '2022-06-14 00:00:00Z',
    '2',
    'personal_tin_id__2'
),
(
    '3',
    'place_id__3_slug',
    'Ресторан "Рыба 3"',
    'rkeeper',
    '2022-06-13 00:00:00Z',
    NULL,
    NULL
)
;

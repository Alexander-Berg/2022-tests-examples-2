INSERT INTO combo_matcher.matchings (
    id,
    orders,
    driver,
    combo_info
)
VALUES
(
    0,
    ARRAY['order_id5', 'order_id6'],
    '{}'::JSONB,
    '{}'::JSONB
),
(
    1,
    ARRAY['order_id3', 'order_id4'],
    '{}'::JSONB,
    '{}'::JSONB
);

INSERT INTO combo_matcher.order_meta (
    order_id,
    zone,
    point,
    point_b,
    created,
    due,
    status,
    matching_id,
    search_parameters,
    allowed_classes,
    lookup,
    callback,
    revision
)
VALUES
(
    'order_id1',
    'moscow',
    '(37.63, 55.74)',
    '(37.64, 55.75)',
    '2020-02-02T00:00:00+00:00',
    '2020-02-02T00:01:00+00:00',
    'idle',
    NULL,
    '{
      "zone_id": "moscow",
      "allowed_classes": ["econom"],
      "point": [37.63, 55.74],
      "order_id": "order_id1"
    }'::JSONB,
    ARRAY['econom']::text[],
    (1,1,1),
    ('{callback_url}?order_id=order_id0&version=1&wave=1', '200 milliseconds', 1),
    1
),
(
    'order_id2',
    'moscow',
    '(37.63, 55.74)',
    '(37.64, 55.75)',
    '2020-02-02T00:00:00+00:00',
    '2020-02-02T00:05:00+00:00',
    'idle',
    NULL,
    '{
      "zone_id": "moscow",
      "allowed_classes": ["econom"],
      "point": [37.63, 55.74],
      "order_id": "order_id2"
    }'::JSONB,
    ARRAY['econom']::text[],
    (1,1,1),
    ('{callback_url}?order_id=order_id1&version=1&wave=1', '200 milliseconds', 1),
    2
),
(
    'order_id3',
    'moscow',
    '(37.63, 55.74)',
    '(37.64, 55.75)',
    '2020-02-02T00:00:00+00:00',
    '2020-02-02T00:06:00+00:00',
    'matched',
    0,
    '{
      "zone_id": "moscow",
      "allowed_classes": ["econom"],
      "point": [37.63, 55.74],
      "order_id": "order_id3"
    }'::JSONB,
    ARRAY['econom']::text[],
    (1,1,1),
    ('{callback_url}?order_id=order_id0&version=1&wave=1', '200 milliseconds', 1),
    1
),
(
    'order_id4',
    'moscow',
    '(37.63, 55.74)',
    '(37.64, 55.75)',
    '2020-02-02T00:00:00+00:00',
    '2020-02-02T00:05:00+00:00',
    'matched',
    0,
    '{
      "zone_id": "moscow",
      "allowed_classes": ["econom"],
      "point": [37.63, 55.74],
      "order_id": "order_id4"
    }'::JSONB,
    ARRAY['econom']::text[],
    (1,1,1),
    ('{callback_url}?order_id=order_id1&version=1&wave=1', '200 milliseconds', 1),
    2
),
(
    'order_id5',
    'moscow',
    '(37.63, 55.74)',
    '(37.64, 55.75)',
    '2020-02-02T00:00:00+00:00',
    '2020-02-02T00:05:03+00:00',
    'matched',
    0,
    '{
      "zone_id": "moscow",
      "allowed_classes": ["econom"],
      "point": [37.63, 55.74],
      "order_id": "order_id5"
    }'::JSONB,
    ARRAY['econom']::text[],
    (1,1,1),
    ('{callback_url}?order_id=order_id0&version=1&wave=1', '200 milliseconds', 1),
    1
),
(
    'order_id6',
    'moscow',
    '(37.63, 55.74)',
    '(37.64, 55.75)',
    '2020-02-02T00:00:00+00:00',
    '2020-02-02T00:08:00+00:00',
    'matched',
    0,
    '{
      "zone_id": "moscow",
      "allowed_classes": ["econom"],
      "point": [37.63, 55.74],
      "order_id": "order_id6"
    }'::JSONB,
    ARRAY['econom']::text[],
    (1,1,1),
    ('{callback_url}?order_id=order_id1&version=1&wave=1', '200 milliseconds', 1),
    2
);

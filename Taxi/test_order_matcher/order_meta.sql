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
    allowed_classes
)
VALUES
(
    'order_id0',
    'moscow',
    '(37.63, 55.74)',
    '(37.64, 55.75)',
    '2021-9-9T01:46:00+00:00',
    '2021-9-9T01:54:00+00:00',
    'idle',
    null,
    '{
      "zone_id": "moscow",
      "allowed_classes": ["econom"],
      "point": [37.63, 55.74],
      "order_id": "order_id0"
    }',
    '{"econom"}'
),
(
    'order_id1',
    'moscow',
    '(37.625, 55.735)',
    '(37.64, 55.75)',
    '2021-9-9T01:45:00+00:00',
    '2021-9-9T01:55:00+00:00',
    'matching',
    null,
    '{
      "zone_id": "moscow",
      "point": [37.63, 55.74],
      "order_id": "order_id1"
    }',
    '{}'
);

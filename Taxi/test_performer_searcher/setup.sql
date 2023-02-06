INSERT INTO combo_matcher.matchings (
  id,
  orders,
  driver,
  combo_info
)
VALUES
(
  0,
  ARRAY['order_id0', 'order_id1'],
  '{{}}',
  '{{}}'
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
  callback
)
VALUES
(
  'order_id0',
  'moscow',
  '(37.63, 55.74)',
  '(37.64, 55.75)',
  '2001-9-9 01:46:39',
  '2001-9-9 01:46:39',
  'matched',
  0,
  '{{
    "zone_id": "moscow",
    "allowed_classes": ["econom"],
    "point": [37.63, 55.74],
    "order_id": "order_id0"
  }}',
  '{{"econom"}}',
  (1,1,1),
  ('{callback_url}?order_id=order_id0&version=1&wave=1', '200 milliseconds', 1)
),
(
  'order_id1',
  'moscow',
  '(37.63, 55.74)',
  '(37.64, 55.75)',
  '2001-9-9 01:46:39',
  '2001-9-9 01:46:39',
  'matched',
  0,
  '{{
    "zone_id": "moscow",
    "allowed_classes": ["econom"],
    "point": [37.63, 55.74],
    "order_id": "order_id1"
  }}',
  '{{"econom"}}',
  (1,1,1),
  ('{callback_url}?order_id=order_id1&version=1&wave=1', '200 milliseconds', 1)
);

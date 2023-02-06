INSERT INTO combo_matcher.order_meta (
  order_id,
  zone,
  point,
  point_b,
  created,
  due,
  matching_id,
  search_parameters,
  status,
  allowed_classes,
  lookup,
  callback
)
VALUES (
  'order_id0', 
  'moscow',
  '(37.64,55.74)',
  '(37.65,55.75)',
  '2022-6-20 01:00:00',
  '2022-6-20 01:10:00',
  NULL,
  '{{}}',
  'assigned',
  '{{"econom"}}',
  (1,1,1),
  ('{callback_url}?order_id=order_id0&version=1&wave=1', '200 milliseconds', 1)
);

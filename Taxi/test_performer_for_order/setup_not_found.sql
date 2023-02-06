INSERT INTO combo_matcher.order_meta (
  order_id,
  zone,
  point,
  point_b,
  created,
  due,
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
  '{}',
  'matched',
  '{"econom"}',
  (1,1,1),
  ('url', '200 milliseconds', 1)
);

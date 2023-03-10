INSERT INTO combo_contractors.customer_order (
  chunk_id,
  order_id,
  dbid_uuid,
  updated,
  taxi_status,
  source,
  destination,
  event_index,
  ready_status,
  tariff_class,
  tariff_zone,
  has_comment,
  calc_alternative_type,
  driving_started_at,
  transporting_started_at
)
VALUES
(
  0,
  'order_id12',
  'dbid_uuid12',
  '2020-05-18T14:05:00.00Z',
  'transporting',
  '(37.0, 55.0)',
  '(37.2, 55.2)',
  0,
  'pending',
  'econom',
  'moscow',
  FALSE,
  NULL,
  '2020-05-18T14:00:00.00Z',
  '2020-05-18T14:05:00.00Z'
),
(
  0,
  'requested_order',
  'dbid_uuid12',
  '2020-05-18T15:00:00.00Z',
  'driving',
  '(37.1, 55.1)',
  '(37.3, 55.3)',
  0,
  'pending',
  'econom',
  'moscow',
  FALSE,
  'combo_outer',
  '2020-05-18T15:00:00.00Z',
  NULL
)

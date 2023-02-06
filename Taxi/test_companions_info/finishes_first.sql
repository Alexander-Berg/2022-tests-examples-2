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
  transporting_started_at,
  driving_started_at,
  combo_info
)
VALUES
(
  0,
  'order_id1',
  'dbid_uuid1',
  '2020-05-18T15:00:00.00Z',
  'transporting',
  '(37.0, 55.0)',
  '(37.2, 55.2)',
  0,
  'pending',
  'econom',
  'moscow',
  FALSE,
  'combo_outer',
  '2020-05-18T15:00:00.00Z',
  '2020-05-18T14:50:00.00Z',
  NULL
),
(
  0,
  'requested_order',
  'dbid_uuid1',
  '2020-05-18T15:00:00.00Z',
  'transporting',
  '(37.1, 55.1)',
  '(37.3, 55.3)',
  0,
  'pending',
  'econom',
  'moscow',
  FALSE,
  'combo_outer',
  '2020-05-18T15:06:00.00Z',
  '2020-05-18T15:03:00.00Z',
  '{
     "route": [
       {
         "position": [37.0, 55.0],
         "order_id": "order_id1",
         "type": "start",
         "passed_at": "2020-05-18T15:00:00.00Z"
       },
       {
         "position": [37.1, 55.1],
         "order_id": "requested_order",
         "type": "start"
       },
       {
         "position": [37.2, 55.2],
         "order_id": "order_id1",
         "type": "finish"
       },
       {
         "position": [37.3, 55.3],
         "order_id": "requested_order",
         "type": "finish"
       }
     ]
  }'
)

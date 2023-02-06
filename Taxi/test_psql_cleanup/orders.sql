INSERT INTO busy_drivers.order_meta (
  order_id, driver_id, updated, destination, 
  taxi_status, order_status, flags, 
  chunk_id, cargo_ref_id
) 
VALUES 
  (
    'order_id0', 'dbid_uuid0', '1969-7-20 23:17:39+03', 
    '(37.66, 55.71)', 'transporting', 
    'skip', '{}', 0, NULL
  ), 
  (
    'order_id1', 'dbid_uuid1', '1969-7-20 23:17:39+03', 
    '(37.66,
       55.71)', 'complete', 
    'finished', '{}', 1, 'cargo_0'
  ), 
  (
    'order_id2', 'dbid_uuid2', '1969-7-20 23:17:39+03',
    '(37.66,
       55.71)', 'complete', 
    'finished', '{}', 2, NULL
  );

INSERT INTO busy_drivers.logistics_events (
  cargo_ref_id, event_type, updated, destinations, destinations_statuses
)
VALUES
  ('cargo_0', 'change', '1969-7-20 23:17:39+03', '{"(37.66, 55.71)"}', '{ false }'),
  ('cargo_1', 'change', '1969-7-20 23:17:39+03', '{"(37.66, 55.71)"}', '{ false }');

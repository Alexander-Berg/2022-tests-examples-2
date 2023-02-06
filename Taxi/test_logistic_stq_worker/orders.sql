INSERT INTO busy_drivers.order_meta (
  order_id, driver_id, updated, taxi_status,
  order_status, flags, chunk_id, 
  destinations, destinations_statuses, cargo_ref_id
)
VALUES
  (
    'order_id0', 'dbid_uuid0', '2004-10-19 10:20:00+03',
    'transporting', 'pending', '{}',
    0, '{ "(55.45,37.36)", "(55.4723,37.3598)" }', '{ false, false }', NULL
  ),
  (
    'order_id1', 'dbid_uuid1', '2004-10-19 10:20:00+03',
    'transporting', 'pending', '{}',
    0, '{ "(55.45,37.36)", "(55.4723,37.3598)" }', '{ false, false }', 'cargo_ref_id'
  )

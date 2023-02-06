INSERT INTO busy_drivers.order_meta (
  order_id, driver_id, updated, taxi_status,
  order_status, flags, chunk_id, destination, final_destination
)
VALUES
  (
    'order_id0', 'dbid_uuid0', '2004-10-19 10:20:00+03',
    'transporting', 'pending', '{}',
    0, '(55.45,37.36)', '(55.4722,37.3597)'
  ),
  (
    'order_id1', 'dbid_uuid0', '2004-10-19 10:21:00+03',
    'driving', 'pending', '{}', 0, NULL, NULL
  ),
  (
    'order_id2', 'dbid_uuid1', '2004-10-19 10:22:00+03',
    'driving', 'pending', '{}', 1, NULL, NULL
  ),
  (
    'order_id3', 'dbid_uuid2', '2004-10-19 10:23:00+03',
    'driving', 'pending', '{}', 2, NULL, NULL
  ),
  (
    'order_id4', 'dbid_uuid3', '2004-10-19 10:24:00+03',
    'waiting', 'pending', '{}', 3, NULL, NULL
  ),
  (
    'order_id5', 'dbid_uuid4', '2004-10-19 10:25:00+03',
    'complete', 'finished', '{}', 4, NULL, NULL
  )

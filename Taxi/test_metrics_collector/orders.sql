INSERT INTO busy_drivers.order_meta (
  order_id, driver_id, updated, destination, 
  taxi_status, order_status, flags, 
  chunk_id
) 
VALUES 
  (
    'order_id0', 'dbid_uuid0', '1969-7-20 20:17:39', 
    '(37.66, 55.71)', 'driving', 
    'pending', '{}', 0
  ), 
  (
    'order_id1', 'dbid_uuid0', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'transporting', 
    'pending', '{}', 1
  ), 
  (
    'order_id2', 'dbid_uuid1', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'complete', 
    'skip', '{}', 2
  ),
  (
    'order_id3', 'dbid_uuid2', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'transporting', 
    'pending', '{}', 1
  ),
  (
    'order_id4', 'dbid_uuid3', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'waiting', 
    'pending', '{}', 1
  ),
  (
    'order_id5', 'dbid_uuid4', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'cancelled', 
    'skip', '{}', 1
  ),
  (
    'order_id6', 'dbid_uuid5', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'driving', 
    'pending', '{}', 1
  ),
  (
    'order_id7', 'dbid_uuid6', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'transporting', 
    'pending', '{}', 1
  ),
  (
    'order_id8', 'dbid_uuid7', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'waiting', 
    'skip', '{}', 1
  ),
  (
    'order_id9', 'dbid_uuid8', '1969-7-20 20:17:39', 
    '(37.66,
       55.71)', 'cancelled', 
    'pending', '{}', 1
  );


SELECT 
  busy_drivers.save_chain_busy_drivers_chunk(
    0, -- chunk_id
    '1969-7-20 20:17:39', -- updated
    ARRAY[ 'dbid_uuid0',
    'dbid_uuid1' ],
    ARRAY[ 'order_id0', 
    'order_id1' ], 
    ARRAY[ '0', 
    '1' ], -- flags
    ARRAY['(55.45,37.36)', '(55.45,37.36)']::point[], -- destination
    ARRAY[100, 200]::bigint[], -- left_time
    ARRAY[1000, 2000]::double precision[], -- left_distance
    ARRAY['route_tracking', 'linear_fallback']::busy_drivers.tracking_type_t[]
  );

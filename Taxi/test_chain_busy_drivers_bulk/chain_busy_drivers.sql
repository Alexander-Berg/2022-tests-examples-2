SELECT 
  busy_drivers.save_chain_busy_drivers_chunk(
    0, -- chunk_id
    '2004-10-19 10:20:00+03', -- updated
    ARRAY['order_id0'], 
    ARRAY['dbid_uuid0'],
    ARRAY['0'], -- flags
    ARRAY['(55.45,37.36)']::point[], -- destination
    ARRAY[100]::bigint[], -- left_time
    ARRAY[1000]::double precision[], -- left_distance
    ARRAY['route_tracking']::busy_drivers.tracking_type_t[]
  ),
  busy_drivers.save_chain_busy_drivers_chunk(
    2,
    '2004-10-19 10:21:00+03',
    ARRAY['order_id1'], 
    ARRAY['dbid_uuid1'],
    ARRAY['1'],
    ARRAY['(55.45,37.36)']::point[],
    ARRAY[200]::bigint[],
    ARRAY[2000]::double precision[],
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  ),
  busy_drivers.save_chain_busy_drivers_chunk(
    4,
    '2004-10-19 10:22:00+03',
    ARRAY['order_id2'], 
    ARRAY['dbid_uuid2'],
    ARRAY['1'],
    ARRAY['(55.45,37.36)']::point[],
    ARRAY[200]::bigint[],
    ARRAY[2000]::double precision[],
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  ),
  busy_drivers.save_chain_busy_drivers_chunk(
    6,
    '2004-10-19 10:23:00+03',
    ARRAY['order_id3'],
    ARRAY['dbid_uuid3'],
    ARRAY['1'],
    ARRAY['(55.45,37.36)']::point[],
    ARRAY[200]::bigint[],
    ARRAY[2000]::double precision[],
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  );

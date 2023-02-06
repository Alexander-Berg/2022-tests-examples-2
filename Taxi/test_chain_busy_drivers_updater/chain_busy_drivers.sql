-- mimick results of route estimate task's previous run
SELECT 
  busy_drivers.save_chain_busy_drivers_chunk(
    0, -- chunk_id 
    '2004-10-19 10:23:54+02', -- updated
    ARRAY['old_order_id0'],
    ARRAY['old_dbid_uuid0'],
    ARRAY['0'], -- flags
    ARRAY['(55.45,37.36)']::point[], -- destination
    ARRAY[100]::bigint[], -- left_time
    ARRAY[100]::double precision[], -- left_distance
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  ),
  busy_drivers.save_chain_busy_drivers_chunk(
    1, 
    '2004-10-19 10:23:54+02', 
    ARRAY['old_order_id1'],
    ARRAY['old_dbid_uuid1'],
    ARRAY['0'],
    ARRAY['(55.45,37.36)']::point[],
    ARRAY[100]::bigint[],
    ARRAY[100]::double precision[],
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  ),
  busy_drivers.save_chain_busy_drivers_chunk(
    2, 
    '2004-10-19 10:23:54+02', 
    ARRAY['old_order_id2'],
    ARRAY['old_dbid_uuid2'],
    ARRAY['0'],
    ARRAY['(55.45,37.36)']::point[],
    ARRAY[100]::bigint[],
    ARRAY[100]::double precision[],
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  ),
  busy_drivers.save_chain_busy_drivers_chunk(
    3, 
    '2004-10-19 10:23:54+02', 
    ARRAY['old_order_id3'],
    ARRAY['old_dbid_uuid3'],
    ARRAY['0'],
    ARRAY['(55.45,37.36)']::point[],
    ARRAY[100]::bigint[],
    ARRAY[100]::double precision[],
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  ),
  busy_drivers.save_chain_busy_drivers_chunk(
    4, 
    '2004-10-19 10:23:54+02', 
    ARRAY['old_order_id4'],
    ARRAY['old_dbid_uuid4'],
    ARRAY['0'],
    ARRAY['(55.45,37.36)']::point[],
    ARRAY[100]::bigint[],
    ARRAY[100]::double precision[],
    ARRAY['linear_fallback']::busy_drivers.tracking_type_t[]
  );

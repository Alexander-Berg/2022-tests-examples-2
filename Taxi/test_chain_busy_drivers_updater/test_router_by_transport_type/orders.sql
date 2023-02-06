INSERT INTO busy_drivers.order_meta (
  order_id, driver_id, updated, destination, 
  taxi_status, order_status, flags, 
  chunk_id, tariff_zone, tariff_class, special_requirements, 
  transport_type
) 
VALUES 
  (
    'order_id1', 'dbid_uuid1', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', 'transporting', 
    'pending', '{}', 1, 'spb', 'econom', '{}', NULL
  ),
  (
    'order_id2', 'dbid_uuid2', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', 'transporting', 
    'pending', '{}', 1, 'spb', 'econom', '{}', 'pedestrian'
  ), 
  (
    'order_id3', 'dbid_uuid3', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', 'transporting', 
    'pending', '{}', 1, 'spb', 'econom', '{}', 'bicycle'
  );

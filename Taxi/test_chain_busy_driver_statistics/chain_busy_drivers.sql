CREATE TABLE IF NOT EXISTS busy_drivers.chain_busy_drivers_chunk_0 
PARTITION OF busy_drivers.chain_busy_drivers FOR VALUES IN (0);

INSERT INTO busy_drivers.chain_busy_drivers_chunk_0 (
  chunk_id, updated, order_id, driver_id, 
  flags, destination, left_time, left_distance, 
  tracking_type, driver_skip_reason, 
  geobus_eta_reject_reason, tariff_zone, 
  tariff_class
) 
VALUES 
  (
    0, '2004-10-19 10:23:54+02', 'order_id0', 
    'driver_id0', '0', '(55.45,37.36)', 
    42, 42, 'route_tracking', 'position_too_old', 
    'missing', 'moscow', 'econom'
  ),
  (
    0, '2004-10-19 10:23:54+02', 'order_id1', 
    'driver_id1', '0', '(55.45,37.36)', 
    42, 42, 'route_tracking', 'position_too_old', 
    'missing', 'spb', 'econom'
  ),
  (
    0, '2004-10-19 10:23:54+02', 'order_id2', 
    'driver_id2', '0', '(55.45,37.36)', 
    42, 42, 'route_tracking', NULL, 
    NULL, 'moscow', 'econom'
  ),
  (
    0, '2004-10-19 10:23:54+02', 'order_id3', 
    'driver_id3', '0', '(55.45,37.36)', 
    42, 42, 'route_tracking', 'position_too_old', 
    'missing', NULL, NULL
  );

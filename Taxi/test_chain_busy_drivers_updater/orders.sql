INSERT INTO busy_drivers.order_meta (
  order_id, driver_id, updated, destination, final_destination,
  taxi_status, order_status, flags, 
  chunk_id, tariff_zone, tariff_class, special_requirements, destinations, destinations_statuses
) 
VALUES 
  (
    'order_id0', 'dbid_uuid0', '2000-7-20 20:17:39', 
    '(37.66, 55.71)', '(37.66, 55.71)', 'transporting', 
    'skip', '{}', 0, 'moscow', 'econom', '{}', NULL, NULL
  ), 
  (
    'order_id1', 'dbid_uuid1', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', NULL, 'transporting', 
    'pending', '{}', 1, 'spb', 'econom', '{}', NULL, NULL
  ), 
  (
    'order_id2', 'dbid_uuid2', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting', 
    'pending', '{}', 2, 'moscow', 'business', '{"thermobag_delivery"}', NULL, NULL
  ),
  (
    'order_id3', 'dbid_uuid3', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting', 
    'pending', '{}', 2, 'moscow', 'cargo', '{}', NULL, NULL
  ),
  (
    'order_id4', 'dbid_uuid4', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting', 
    'pending', '{}', 2, 'tula', 'econom', '{}', NULL, NULL
  ),
  (
    'order_id5', 'dbid_uuid5', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting', 
    'finished', '{}', 3, 'moscow', 'business', '{}', NULL, NULL
  ),
  (
    'order_id6', 'dbid_uuid6', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting',
    'pending', '{}', 1, 'spb', 'econom', '{"thermobag_delivery"}', NULL, NULL
  ),
  (
    'order_id7', 'dbid_uuid7', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting',
    'pending', '{}', 1, 'spb', 'econom', '{"child_seat"}', NULL, NULL
  ),
  (
    'order_id8', 'dbid_uuid8', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting', 
    'pending', '{}', 2, 'moscow', 'business', '{"thermobag_delivery", "child_seat"}', NULL, NULL
  ),
  (
    'order_id9', 'dbid_uuid9', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'transporting', 
    'pending', '{}', 1, 'spb', 'econom', '{}', NULL, NULL
  ), 
  (
    'order_id10', 'dbid_uuid9', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', '(37.66, 55.71)', 'driving', 
    'pending', '{}', 1, 'spb', 'econom', '{}', NULL, NULL
  ),
  (
    'order_id11', 'dbid_uuid10', '2000-7-20 20:17:39', 
    '(37.66,
       55.71)', NULL, 'transporting', 
    'pending', '{}', 1, 'spb', 'econom', '{}', '{ "(37.66,55.71)" }', ' { false }'
  ),
  (
    'order_id12', 'dbid_uuid10', '2000-7-20 20:17:39', 
    NULL, NULL, 'transporting',
    'pending', '{}', 1, 'spb', 'econom', '{}', '{ "(37.66,55.71)" }', ' { false }'
  );

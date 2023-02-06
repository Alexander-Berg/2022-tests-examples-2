INSERT INTO combo_contractors.customer_order (
  order_id, dbid_uuid, updated, taxi_status, 
  destination, chunk_id, event_index, ready_status, 
  tariff_class, tariff_zone, has_comment, source, calc_alternative_type
) 
VALUES
  (
    'order_id1', 'dbid_uuid1', '2001-9-9 01:46:39', 
    'transporting', '(37.66, 55.71)',
    0, 2, 'pending', 'econom', 'moscow', 
    FALSE, '(37.66, 55.71)', 'combo_outer'
  ), 
  (
    'order_id2', 'dbid_uuid2', '2001-9-9 01:46:39', 
    'transporting', '(37.66, 55.71)',
    0, 1, 'pending', 'econom', 'moscow', 
    FALSE, '(37.66, 55.71)', 'combo_outer'
  );

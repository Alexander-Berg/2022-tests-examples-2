INSERT INTO combo_contractors.contractor (
  chunk_id, dbid_uuid, order_id, updated, position,
  source, destination, left_time, left_distance,
  tariff_class, tariff_zone, calc_alternative_type,
  promised_timestamp, combo_info
)
VALUES 
(
  0, 'dbid_uuid0', 'order_id0', '2001-9-9 01:46:39', 
  '(37.66, 55.71)', '(37.66, 55.71)', '(37.66, 55.71)', '00:10:00', 3000.0, 
  '', '', '', '2001-9-9 01:56:39', NULL
),
(
  0, 'dbid_uuid1', 'order_id1', '2001-9-9 01:46:39', 
  '(37.66, 55.71)', '(37.66, 55.71)', '(37.66, 55.71)', '00:10:00', 3000.0, 
  '', '', '', '2001-9-9 01:56:39', NULL
),
(
  1, 'dbid_uuid2', 'order_id2', '2001-9-9 01:46:39', 
  '(37.66, 55.71)', '(37.66, 55.71)', '(37.66, 55.71)', '00:10:00', 3000.0, 
  '', '', '', '2001-9-9 01:56:39', NULL
);

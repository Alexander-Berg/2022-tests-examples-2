INSERT INTO combo_contractors.customer_order (
  order_id, dbid_uuid, updated, taxi_status,
  destination, chunk_id, event_index, ready_status,
  tariff_class, tariff_zone, has_comment, source, calc_alternative_type,
  user_phone_id, plan_transporting_time, plan_transporting_distance,
  payment_type, corp_client_id, transporting_started_at, combo_info
)
VALUES
  (
    'order_id0', 'dbid_uuid0', '2001-9-9 01:46:00',
    'transporting', '(37.11, 55.22)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.33, 55.44)', 'combo',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', '2001-9-9 01:44:00',
    NULL
  );

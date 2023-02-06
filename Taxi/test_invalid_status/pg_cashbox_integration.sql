INSERT INTO cashbox_integration.receipts(
  park_id, 
  driver_id,
  order_id,
  cashbox_id,
  external_id,
  status,
  created_at,
  updated_at
) VALUES
(
  'park_id_1',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'idempotency_key_1',
  'push_to_cashbox',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);

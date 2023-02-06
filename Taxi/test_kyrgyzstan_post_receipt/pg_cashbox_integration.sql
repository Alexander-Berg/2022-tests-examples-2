INSERT INTO cashbox_integration.receipts(
  park_id,
  driver_id,
  order_id,
  cashbox_id,
  external_id,
  status,
  created_at,
  updated_at,
  order_price,
  order_end
)
VALUES (
  'park_id_1',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'idempotency_key_1',
  'push_to_cashbox',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP,
  '250.00',
  '2019-10-01T10:10:00'
);

INSERT INTO cashbox_integration.cashboxes(
  park_id,
  id,
  idempotency_token,
  date_created,
  date_updated,
  state,
  is_current,
  cashbox_type,
  details,
  secrets
)
VALUES (
  'park_id_1',
  'cashbox_id_1',
  'idemp_1',
  '2019-06-22 19:10:25-07',
  '2019-06-22 19:10:25-07',
  'valid',
  'TRUE',
  'kyrgyzstan',
  '{
  }',
  '{
      "uuid": "M5a7svvcrnA7E5axBDY2sw=="
  }'
);

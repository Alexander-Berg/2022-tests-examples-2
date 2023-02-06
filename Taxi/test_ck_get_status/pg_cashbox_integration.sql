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
  order_end,
  task_uuid,
  order_end_point
)
VALUES (
  'park_id_1',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'idempotency_key_1',
  'wait_status',
  '2019-10-01T10:05:00',
  '2019-10-01T10:05:00',
  '250.00',
  '2019-10-01T10:10:00',
  'uuid_1',
  '(10.01, 20.01)'
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
  'cloud_kassir',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple"
  }',
  '{
      "public_id": "M5a7svvcrnA7E5axBDY2sw==", 
      "api_secret": "dCKumeJhRuUkLWmKppFyPQ=="
  }'
);

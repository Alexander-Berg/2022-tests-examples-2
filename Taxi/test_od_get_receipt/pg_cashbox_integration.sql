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
  task_uuid
)
VALUES (
  'park_id_1',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'uuid_1',
  'wait_status',
  '2019-10-01T10:05:00',
  '2019-10-01T10:05:00',
  '250.00',
  '2019-10-01T10:10:00',
  'uuid_1'
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
  'orange_data',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple"
  }',
  '{
      "signature_private_key": "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"
  }'
);

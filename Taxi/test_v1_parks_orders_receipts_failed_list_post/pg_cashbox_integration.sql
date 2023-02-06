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
  failure_id
)
VALUES (
  'park_id_1',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'idempotency_key_1',
  'expired',
  '2019-10-01T10:11:00+00:00',
  '2019-10-01T10:16:00+00:00',
  '250.00',
  '2019-10-01T10:10:00+00:00',
  'kUnknownInn'
),
(
  'park_id_1',
  'driver_id_1',
  'order_id_2',
  'cashbox_id_1',
  'idempotency_key_2',
  'complete',
  '2019-10-01T10:11:00+00:00',
  '2019-10-01T10:16:00+00:00',
  '250.00',
  '2019-10-01T10:10:00+00:00',
  NULL
),
(
  'park_id_1',
  'driver_id_1',
  'order_id_3',
  'cashbox_id_1',
  'idempotency_key_3',
  'fail',
  '2019-10-01T10:12:00+00:00',
  '2019-10-01T10:16:00+00:00',
  '250.00',
  '2019-10-01T10:10:00+00:00',
  'kUuidNotFound'
),
(
  'park_id_2',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'idempotency_key_4',
  'fail',
  '2019-10-01T10:13:00+00:00',
  '2019-10-01T10:16:00+00:00',
  '250.00',
  '2019-10-01T10:10:00+00:00',
  'kUuidNotFound'
),
(
  'park_id_3',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'idempotency_key_5',
  'fail',
  '2019-10-01T10:13:00+00:00',
  '2019-10-01T10:16:00+00:00',
  '250.00',
  '2019-10-01T10:10:00+00:00',
  NULL
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
  'atol_online',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple",
      "group_code": "group-code-1"
  }',
  '{
      "login": "N9Ih+w8vaAoBkF3PpUxXnw==",
      "password": "8Ay7OVs/82E0EnKqEKqKqw=="
  }'
),
(
  'park_id_3',
  'cashbox_id_1',
  'idemp_1',
  '2019-06-22 19:10:25-07',
  '2019-06-22 19:10:25-07',
  'valid',
  'TRUE',
  'atol_online',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple",
      "group_code": "group-code-1"
  }',
  '{
      "login": "N9Ih+w8vaAoBkF3PpUxXnw==",
      "password": "8Ay7OVs/82E0EnKqEKqKqw=="
  }'
);

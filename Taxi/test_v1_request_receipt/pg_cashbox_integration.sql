INSERT INTO cashbox_integration.receipts(
  park_id,
  driver_id,
  order_id,
  cashbox_id,
  external_id,
  status,
  created_at,
  updated_at
)
VALUES (
  'park_id_1',
  'driver_id_1',
  'order_id_2',
  'cashbox_id_1',
  'idempotency_key_1',
  'need_order_info',
  '2019-10-01T10:05:00',
  '2019-10-01T10:05:00'
);

INSERT INTO cashbox_integration.cashboxes
VALUES (
  'park_id_1',
  'cashbox_id_1',
  'idempotency_token_key_1',
  '2016-06-22 19:10:25-07',
  '2016-06-22 19:10:25-07',
  'valid',
  TRUE,
  'atol_online',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple",
      "group_code": "super_park_group"
  }',
  '{
      "login": "M5a7svvcrnA7E5axBDY2sw==",
      "password": "dCKumeJhRuUkLWmKppFyPQ=="
  }'
),
(
  'park_id_2',
  'cashbox_id_2',
  'idempotency_token_key_2',
  '2016-06-22 19:10:25-07',
  '2016-06-22 19:10:25-07',
  'valid',
  TRUE,
  'atol_online',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple",
      "group_code": "super_park_group"
  }',
  '{
      "login": "M5a7svvcrnA7E5axBDY2sw==",
      "password": "dCKumeJhRuUkLWmKppFyPQ=="
  }'
);

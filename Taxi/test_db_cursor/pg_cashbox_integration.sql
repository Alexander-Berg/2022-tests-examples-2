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
) VALUES
(
  'park_id_1',
  'driver_id_1',
  'order_id_1',
  'cashbox_id_1',
  'key1',
  'push_to_cashbox',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP,
  '250.00',
  '2019-10-01T10:10:00',
  NULL
),
(
  'park_id_1',
  'driver_id_1',
  'order_id_3',
  'cashbox_id_1',
  'key3',
  'push_to_cashbox',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP + interval '1 minute',
  '250.00',
  '2019-10-01T10:10:00',
  NULL
),
(
  'park_id_1',
  'driver_id_1',
  'order_id_2',
  'cashbox_id_1',
  'key2',
  'push_to_cashbox',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP + interval '1 minute',
  '250.00',
  '2019-10-01T10:10:00',
  NULL
),
(
  'park_id_1',
  'driver_id_1',
  'order_id_4',
  'cashbox_id_1',
  'key4',
  'wait_status',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP + interval '4 minute',
  '250.00',
  '2019-10-01T10:10:00',
  'uuid_4'
),
(
  'park_id_1',
  'driver_id_1',
  'order_id_6',
  'cashbox_id_1',
  'key6',
  'wait_status',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP + interval '5 minute',
  '250.00',
  '2019-10-01T10:10:00',
  'uuid_6'
),
(
  'park_id_1',
  'driver_id_1',
  'order_id_5',
  'cashbox_id_1',
  'key5',
  'wait_status',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP + interval '5 minute',
  '250.00',
  '2019-10-01T10:10:00',
  'uuid_5'
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
VALUES
(
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

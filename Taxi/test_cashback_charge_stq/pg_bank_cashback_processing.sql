INSERT INTO bank_cashback_processing.cashbacks(
  idempotency_token,
  direction,
  cashback_type,
  bank_uid,
  yandex_uid,
  amount,
  currency,
  purchase_token,
  trust_payload
)
VALUES (
         'd9abbfb7-84d4-44be-94b3-8f8ea7eb31df',
         'TOPUP'::bank_cashback_processing.cashback_direction_t,
         'TRANSACTION'::bank_cashback_processing.cashback_type_t,
         'bank_uid',
         'yandex_uid',
         '100',
         'RUB',
         'purchase_token',
         '{"pass_params": {"payload": {"has_plus": true}},
           "developer_payload": {"rule_id": "rule_id"}}'::jsonb
       ),
       (
         '2',
         'TOPUP'::bank_cashback_processing.cashback_direction_t,
         'TRANSACTION'::bank_cashback_processing.cashback_type_t,
         'bank_uid',
         'yandex_uid',
         '100',
         'RUB',
         NULL,
         '{"pass_params": {"payload": {"has_plus": true}},
           "developer_payload": {"rule_id": "rule_id"}}'::jsonb
       ),
       (
         'transaction_transaction_id',
         'TOPUP'::bank_cashback_processing.cashback_direction_t,
         'TRANSACTION'::bank_cashback_processing.cashback_type_t,
         'bank_uid',
         'yandex_uid',
         '100',
         'RUB',
         NULL,
         '{"pass_params": {"payload": {"has_plus": true}},
           "developer_payload": {"rule_id": "rule_id"}}'::jsonb
       );

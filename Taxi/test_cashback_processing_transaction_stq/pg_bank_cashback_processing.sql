INSERT INTO bank_cashback_processing.cashbacks(
  idempotency_token,
  direction,
  cashback_type,
  bank_uid,
  yandex_uid,
  amount,
  currency,
  purchase_token,
  status
)
VALUES ('d9abbfb7-84d4-44be-94b3-8f8ea7eb31df',
        'TOPUP'::bank_cashback_processing.cashback_direction_t,
        'TRANSACTION'::bank_cashback_processing.cashback_type_t,
        'bank_uid',
        'yandex_uid',
        '100',
        'RUB',
        'purchase_token',
        'PAYMENT_RECEIVED');

INSERT INTO bank_cashback_processing.transaction_cashbacks (
  transaction_id,
  rule_id,
  cashback_idempotency_token
) VALUES (
  'static_transaction_id',
  '1',
  'd9abbfb7-84d4-44be-94b3-8f8ea7eb31df'
);

INSERT INTO bank_cashback_processing.calculated_transactions (
  transaction_id,
  type,
  timestamp,
  currency,
  amount,
  rule_ids,
  transaction_info,
  bank_uid,
  yandex_uid
) VALUES (
 'static_transaction_id',
 'PURCHASE',
 '1970-01-28T12:08:48.372+03:00',
 'RUB',
 '100.0000',
 '{{"id_1"}}',
 '{"order_id":"service_order_id",
   "trust_service_id":"trust_service_id",
   "merchant_name":"merchant_name",
   "mcc":"mcc"}'::jsonb,
  'bank_uid',
  'yandex_uid'
);

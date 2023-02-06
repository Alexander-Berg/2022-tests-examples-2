INSERT INTO card_antifraud.cards_verification (
    yandex_uid,
    device_id,
    card_id,
    status,
    method,
    purchase_token,
    created_at,
    updated_at,
    trust_verification_id,
    idempotency_token
  )
VALUES
  (
    '1235',
    'device_1235_1',
    'card-x1235',
    '3ds_required',
    'standard2_3ds',
    'purchase_1235',
    '2020-01-31 00:00:00+00',
    '2020-01-31 00:00:00+00',
    'purchase_1235',
    'idempotency_1235_1'
  ),
  (
    '1236',
    'device_1236_1',
    'card-x1236',
    '3ds_required',
    'standard2_3ds',
    'purchase_1236',
    '2020-02-02 00:00:00+00',
    '2020-02-02 00:00:00+00',
    'purchase_1236',
    'idempotency_1236_1'
  );

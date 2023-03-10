INSERT INTO card_antifraud.cards_verification (
    yandex_uid,
    device_id,
    card_id,
    status,
    method,
    purchase_token,
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
    'purchase_1235',
    'idempotency_1235_1'
  ),
  (
    '1235',
    'device_1235_1',
    'card-x1235',
    '3ds_status_received',
    'standard2_3ds',
    'purchase_1235',
    'purchase_1235',
    'idempotency_1235_2'
  ),
  (
    '1235',
    'device_1235_2',
    'card-x1235',
    'in_progress',
    'standard2_3ds',
    'purchase_1235',
    'purchase_1235',
    'idempotency_1235_3'
  ),
  (
    '1234',
    'test_id',
    'card-x1234567',
    'in_progress',
    'standard2',
    'temp_id1',
    'temp_id1',
    'test_token'
  );

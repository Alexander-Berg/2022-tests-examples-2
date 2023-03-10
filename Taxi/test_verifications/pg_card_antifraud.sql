INSERT INTO card_antifraud.cards_verification (
    yandex_uid,
    device_id,
    card_id,
    status,
    method,
    purchase_token,
    trust_verification_id,
    idempotency_token,
    version
  )
VALUES
  (
    '1235',
    'test_id',
    'card-x1234568',
    'in_progress',
    'standard2',
    'temp_id1',
    'temp_id1',
    'test_token',
    1
  ),
  (
    '1235',
    '',
    'card-x1234568',
    'in_progress',
    'standard2',
    'temp_id1',
    'temp_id1',
    'test_token',
    1
  );

INSERT INTO card_antifraud.cards_verification (
    yandex_uid,
    device_id,
    card_id,
    status,
    method,
    idempotency_token,
    version
  )
VALUES
  (
    '1236',
    'test_id',
    'card-x1234568',
    'in_progress',
    'standard2',
    'test_token',
    1
  ),
  (
    '1236',
    '',
    'card-x1234568',
    'in_progress',
    'standard2',
    'test_token',
    1
  );

INSERT INTO card_antifraud.cards_verification (
    yandex_uid,
    device_id,
    card_id,
    status,
    idempotency_token
  )
VALUES
  (
    '1235',
    'test_id',
    'card-x1234567',
    'draft',
    'test_token1'
  ),
  (
    '1235',
    '',
    'card-x1234567',
    'draft',
    'test_token1'
  );

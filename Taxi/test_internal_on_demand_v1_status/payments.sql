
INSERT INTO
  pay.payments (
    payment_id,
    balance_id,
    clid,
    doc_id,
    created_at,
    updated_at,
    origin,
    status,
    status_date
  )
VALUES
  (
    'PAYMENT01',
    'BALANCE01',
    'CLID01',
    67521601301,
    '2021-01-01T11:00+03:00',
    '2021-01-01T11:00+03:00',
    'scheduled',
    'created',
    '2021-01-01T11:00+03:00'
  ),
  (
    'PAYMENT06',
    'BALANCE06',
    'CLID06',
    67521601306,
    '2021-01-01T11:00+03:00',
    '2021-01-01T11:00+03:00',
    'scheduled',
    'pending',
    '2021-01-01T11:00+03:00'
  );

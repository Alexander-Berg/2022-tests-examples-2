INSERT INTO
  pay.payments (
    payment_id,
    clid,
    balance_id,
    created_at,
    updated_at,
    status,
    doc_id
  )
VALUES
  (
    'PAYMENT00',
    'CLID00',
    '75054400',
    '2020-03-20T15:00:00+03:00',
    '2020-03-20T18:00:00+03:00',
    'pending',
    6752160133
  );

INSERT INTO
  pay.payment_entries (
    payment_id,
    contract_id,
    bcid,
    amount,
    currency
  )
VALUES
  (
    'PAYMENT00',
    '278761',
    '32511442',
    '4232.21',
    'RUB'
  ),
  (
    'PAYMENT00',
    '656839',
    '55966500',
    '423.21',
    'EUR'
  ),
  (
    'PAYMENT00',
    '679178',
    '32511442',
    '703.0',
    'EUR'
  ),
  (
    'PAYMENT00',
    '844463',
    '30429664',
    '19660.8',
    'RUB'
  );

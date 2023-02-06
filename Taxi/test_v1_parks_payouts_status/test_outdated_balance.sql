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
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T21:00:00+03:00',
    'completed',
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
  );

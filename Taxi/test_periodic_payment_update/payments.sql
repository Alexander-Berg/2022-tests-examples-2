INSERT INTO pay.payments (
  payment_id,
  clid,
  balance_id,
  created_at,
  updated_at,
  status,
  doc_id
) VALUES
  (
    'PAYMENT00',
    'CLID00',
    '76000000',
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T18:10:00+03:00',
    'pending',
    4870000000
  ),
  (
    'PAYMENT01',
    'CLID01',
    '76000000',
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T17:50:00+03:00',
    'pending',
    4871000000
  ),
  (
    'PAYMENT02',
    'CLID02',
    '76000000',
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T17:40:00+03:00',
    'pending',
    4872000000
  ),
  (
    'PAYMENT03',
    'CLID03',
    '76000000',
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T18:00:00+03:00',
    'pending',
    4873000000
  ),
  (
    'PAYMENT04',
    'CLID04',
    '76000000',
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T18:00:00+03:00',
    'created',
    NULL
  ),
  (
    'PAYMENT05',
    'CLID05',
    '76000000',
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T18:10:00+03:00',
    'created',
    NULL
  ),
  (
    'PAYMENT06',
    'CLID06',
    '76000000',
    '2020-03-21T15:00:00+03:00',
    '2020-03-21T18:10:00+03:00',
    'pending',
    4874000000
  );

INSERT INTO pay.payment_entries (
  payment_id,
  contract_id,
  bcid,
  amount,
  currency
) VALUES
  (
    'PAYMENT00',
    '800000',
    '30000000',
    '9999.99',
    'RUB'
  ),
  (
    'PAYMENT00',
    '800001',
    '30000001',
    '1000.01',
    'USD'
  ),
  (
    'PAYMENT00',
    '800002',
    '30000002',
    '7777777777777777.77',
    'EUR'
  ),
  (
    'PAYMENT01',
    '810000',
    '31000000',
    '9999.99',
    'RUB'
  ),
  (
    'PAYMENT01',
    '810001',
    '31000001',
    '1000.01',
    'USD'
  ),
  (
    'PAYMENT01',
    '810002',
    '31000002',
    '7777777777777777.77',
    'EUR'
  ),
  (
    'PAYMENT02',
    '820000',
    '32000000',
    '0.01',
    'RUB'
  ),
  (
    'PAYMENT03',
    '830000',
    '33000000',
    '0.01',
    'RUB'
  ),
  (
    'PAYMENT06',
    '840000',
    '34000000',
    '0.01',
    'RUB'
  );

INSERT INTO pay.payment_timers (
  clid,
  expires_at
) VALUES (
  'CLID06',
  '2020-03-30T02:00:00+03:00'
)

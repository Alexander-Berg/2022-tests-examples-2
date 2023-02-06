INSERT INTO
  pay.balances (
    balance_id,
    date,
    clid,
    bcid,
    contract_id,
    contract_type,
    contract_alias,
    contract_limit,
    amount,
    currency,
    request_flag,
    org_id,
    reject_code,
    reject_reason
  )
VALUES
  -- No balance entries for CLID00
  (
    '75054400', '2020-03-21T13:30:00+03:00', 'CLID01', '34501203',
    '293599', 'PROMOCODES', 'ОФ-69450/17', '0.0', '75927.48', 'RUB',
    'Y', 'ORG', NULL, NULL
  );

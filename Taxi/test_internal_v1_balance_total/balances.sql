
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
  (
    '75054400', '2020-01-01T12:00:00+03:00', 'CLID00', '7151963',
    '253207', 'CONTRACT_TYPE', 'CONTRACT_ALIAS', '0.0', '100.00', 'RUB',
    'Y', 'ORG', 'N_CONTRACT_ORIGINAL_NOT_PRESENT', 'Отсутствует оригинал договора.'
  ),
  (
    '75054400', '2020-01-01T12:00:00+03:00', 'CLID00', '7151963',
    '253208', 'CONTRACT_TYPE', 'CONTRACT_ALIAS', '0.0', '200.00', 'RUB',
    'Y', 'ORG', NULL, NULL
  ),
  (
    '75054400', '2020-01-01T12:00:00+03:00', 'CLID01', '8151963',
    '353207', 'CONTRACT_TYPE', 'CONTRACT_ALIAS', '0.0', '100.00', 'RUB',
    'Y', 'ORG', NULL, NULL
  ),
  (
    '75054400', '2020-01-01T12:00:00+03:00', 'CLID01', '8151963',
    '353208', 'CONTRACT_TYPE', 'CONTRACT_ALIAS', '0.0', '5.00', 'EUR',
    'Y', 'ORG', NULL, NULL
  );

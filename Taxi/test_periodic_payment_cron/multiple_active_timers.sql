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
    '75054400', '2020-03-21T13:30:00+03:00', 'CLID00', '34501203',
    '293599', 'PROMOCODES', 'ОФ-69450/17', '0.0', '10000.00', 'RUB',
    'Y', 'ORG', NULL, NULL
  ),
  -- No balance entries for CLID01
  (
    '75054400', '2020-03-21T13:30:00+03:00', 'CLID02', '34501203',
    '293599', 'PROMOCODES', 'ОФ-69450/17', '0.0', '30000.00', 'RUB',
    'Y', 'ORG', NULL, NULL
  ),
  -- No balance entries for CLID03
  (
    '75054400', '2020-03-21T13:30:00+03:00', 'CLID04', '34501203',
    '293599', 'PROMOCODES', 'ОФ-69450/17', '0.0', '50000.00', 'RUB',
    'Y', 'ORG', NULL, NULL
  );
  -- No balance entries for CLID05

INSERT INTO
  pay.payment_timers (
    clid,
    expires_at
  )
VALUES
  (
    'CLID00',
    '2020-03-21T13:00:00+03:00'
  ),
  (
    'CLID01',
    '2020-03-21T13:01:00+03:00'
  ),
  (
    'CLID02',
    '2020-03-21T13:02:00+03:00'
  ),
  (
    'CLID03',
    '2020-03-21T13:03:00+03:00'
  ),
  (
    'CLID04',
    '2020-03-21T13:04:00+03:00'
  ),
  (
    'CLID05',
    '2020-03-21T13:05:00+03:00'
  ),
  (
    'CLID06',
    '2020-03-21T13:06:00+03:00'
  );

INSERT INTO
  pay.partner_payout_mode_changes (
    clid,
    active_since,
    active_mode
  )
VALUES
  (
    'CLID05',
    '2020-03-21T13:04:00+03:00',
    'on_demand'
  ),
  (
    'CLID06',
    '2020-03-21T13:04:00+03:00',
    'regular'
  );

INSERT INTO
  fleet_payouts.fleet_statistics (
    clid,
    created_at,
    updated_at,
    partner_country,
    partner_city,
    partner_type,
    recent_work_time,
    recent_cars
  )
VALUES
  (
    'CLID05',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'self_employed',
    0,
    0
  ),
  (
    'CLID06',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'self_employed',
    0,
    0
  );

INSERT INTO
  fleet_payouts.fleet_version_changes
    (
      clid,
      created_at,
      created_by,
      active_since,
      active_version
    )
VALUES
  (
    'CLID00',
    '2019-12-31T12:00:00+03:00',
    '1000',
    '2019-01-01T00:00:00+03:00',
    'basic'
  ),
  (
    'CLID01',
    '2019-12-31T12:00:00+03:00',
    '1000',
    '2019-01-01T00:00:00+03:00',
    'basic'
  );

INSERT INTO
  pay.payment_timers (
    clid,
    expires_at
  )
VALUES
  (
    'CLID00',
    '2020-01-07T14:00:00+03:00'
  ),
  (
    'CLID01',
    '2020-01-07T14:00:00+03:00'
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
    'CLID00',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'legal_entity',
    0,
    0
  ),
  (
    'CLID01',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'self_employed',
    0,
    0
  )

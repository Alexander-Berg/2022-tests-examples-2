
INSERT INTO
  pay.payment_timers (
    expires_at,
    clid
  )
VALUES
  (
    '2021-01-31T03:00+03:00',
    'CLID00'
  ),
  (
    '2021-01-02T03:00+03:00',
    'CLID01'
  );

INSERT INTO 
  pay.partner_payout_mode_changes (
    clid,
    active_since,
    active_mode
  )
VALUES
  (
    'CLID00',
    '2021-01-01T10:00+03:00',
    'on_demand'
  ),
  (
    'CLID01',
    '2021-01-01T10:00+03:00',
    'on_demand'
  ),
  (
    'CLID03',
    '2021-01-01T10:00+03:00',
    'regular'
  );


-- longer payout-mode version history with one wrong value
INSERT INTO 
  pay.partner_payout_mode_changes (
    clid,
    active_since,
    active_mode
  )
VALUES
  (
    'CLID04',
    '2020-01-01T10:00+03:00',
    'regular'
  ),
  (
    'CLID04',
    '2021-01-01T10:00+03:00',
    'on_demand'
  ),
  (
    'CLID04',
    '2022-01-01T10:00+03:00',
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
    'CLID00',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'self_employed',
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
  ),
  (
    'CLID02',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'legal_entity',
    0,
    0
  ),
  (
    'CLID03',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'self_employed',
    0,
    0
  ),
  (
    'CLID04',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'RUS',
    'MOSCOW',
    'self_employed',
    0,
    0
  );


INSERT INTO
  fleet_payouts.fleet_subscription_level_changes
    (
      clid,
      created_at,
      active_since,
      active_level
    )
VALUES
  (
    'CLID00',
    '2020-01-01T12:00:00+03:00',
    '2020-01-02T00:00:00+03:00',
    'LEVEL1'
  ),
  (
    'CLID00',
    '2020-02-01T12:00:00+03:00',
    '2020-02-02T00:00:00+03:00',
    'LEVEL2'
  ),
  (
    'CLID00',
    '2020-03-01T12:00:00+03:00',
    '2020-03-02T00:00:00+03:00',
    'LEVEL3'
  );

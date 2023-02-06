
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
    '2020-01-01T12:00:00+03:00',
    '9000',
    '2020-01-02T00:00:00+03:00',
    'simple'
  ),
  (
    'CLID00',
    '2020-03-01T12:00:00+03:00',
    '9000',
    '2020-03-02T00:00:00+03:00',
    'basic'
  );

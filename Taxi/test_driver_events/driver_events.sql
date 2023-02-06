INSERT INTO dispatch_airport.driver_events (
  udid,
  event_id,
  event_type,

  driver_id,
  airport_id,
  inserted_ts
) VALUES
(
  'udid0',
  'old_session_id0',
  'entered_on_order',

  'dbid0_uuid0',
  'ekb',
  NOW()
),
(
  'udid2',
  'old_session_id2',
  'entered_on_order',

  'dbid2_uuid2',
  'ekb',
  NOW() - INTERVAL '31 minutes'
),
(
  'udid4',
  'old_session_id4',
  'entered_on_repo',

  'dbid4_uuid4',
  'ekb',
  NOW()
),
(
  'udid5',
  'old_session_id5',
  'entered_on_repo',

  'dbid5_uuid5',
  'ekb',
  NOW() - INTERVAL '31 minutes'
),
(
  'udid6',
  'old_session_id6',
  'filtered_by_forbidden_reason',


  'dbid6_uuid6',
  'ekb',
  NOW() - INTERVAL '31 minutes'
),
(
  'udid6',
  'new_session_id6',
  'entered_on_order',


  'dbid6_uuid6',
  'ekb',
  NOW()
),
(
  'udid7',
  'old_session_id7',
  'filtered_by_forbidden_reason',

  'dbid7_uuid7',
  'ekb',
  NOW()
);

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

  'dbid_uuid0',
  'ekb',
  NOW() - INTERVAL '15 minutes'
),
(
  'udid1',
  'old_session_id1',
  'entered_on_repo',

  'dbid_uuid1',
  'ekb',
  NOW() - INTERVAL '15 minutes'
),
(
  'udid2',
  'old_old_session_id2',
  'entered_on_order',

  'dbid_uuid2',
  'ekb',
  NOW() - INTERVAL '20 minutes'
),
(
  'udid2',
  'old_session_id2',
  'filtered_by_forbidden_reason',

  'dbid_uuid2',
  'ekb',
  NOW() - INTERVAL '15 minutes'
),
(
  'udid3',
  'old_session_id3',
  'filtered_by_forbidden_reason',

  'dbid_uuid3',
  'ekb',
  NOW()
),
(
  'udid4',
  'old_old_old_session_id4',
  'entered_on_order',

  'dbid_uuid4',
  'ekb',
  NOW() - INTERVAL '15 minutes'
),
(
  'udid4',
  'old_old_session_id4',
  'filtered_by_forbidden_reason',

  'dbid_uuid4',
  'ekb',
  NOW() - INTERVAL '10 minutes'
),
(
  'udid4',
  'old_session_id4',
  'entered_on_repo',

  'dbid_uuid4',
  'ekb',
  NOW() - INTERVAL '5 minutes'
),
(
  'udid4',
  'old_session_id4',
  'relocate_offer_created',

  'dbid_uuid4',
  'ekb',
  NOW() - INTERVAL '1 minute'
),
(
  'udid5',
  'old_session_id5',
  'entered_on_repo',

  'dbid_uuid5',
  'ekb',
  NOW() - INTERVAL '5 minutes'
),
(
  'udid11',
  'old_session_id11',
  'entered_on_order',

  'dbid_uuid11',
  'ekb',
  NOW() - INTERVAL '15 minutes'
),
(
  'udid13',
  'old_session_id13',
  'entered_on_order',

  'dbid_uuid13',
  'ekb',
  NOW() - INTERVAL '15 minutes'
),
(
  'udid14',
  'old_session_id14',
  'entered_on_order_wrong_client',

  'dbid_uuid14',
  'ekb',
  NOW() - INTERVAL '15 minutes'
);

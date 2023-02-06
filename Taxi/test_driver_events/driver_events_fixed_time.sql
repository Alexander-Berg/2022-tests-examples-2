INSERT INTO dispatch_airport.driver_events (
  udid,
  event_id,
  event_type,

  driver_id,
  airport_id,
  inserted_ts,
  details
) VALUES
(
  'udid0',
  'old_session_id0',
  'entered_on_order',

  'dbid0_uuid0',
  'ekb',
  '2021-06-04T13:37:02.08513+00:00',
  NULL
),
(
  'udid2',
  'old_session_id2',
  'entered_on_order',

  'dbid2_uuid2',
  'ekb',
  '2021-06-04T13:06:02.08513+00:00',
  NULL
),
(
  'udid4',
  'old_session_id4',
  'entered_on_repo',

  'dbid4_uuid4',
  'ekb',
  '2021-06-04T13:37:02.08513+00:00',
  NULL
),
(
  'udid5',
  'old_session_id5',
  'entered_on_repo',

  'dbid5_uuid5',
  'ekb',
  '2021-06-04T13:06:02.08513+00:00',
  NULL
),
(
  'udid6',
  'old_session_id6',
  'filtered_by_forbidden_reason',

  'dbid6_uuid6',
  'ekb',
  '2021-06-04T13:06:02.08513+00:00',
  '{}'::JSONB
),
(
  'udid6',
  'new_session_id6',
  'entered_on_order',

  'dbid6_uuid6',
  'ekb',
  '2021-06-04T13:37:02.08513+00:00',
  '{
    "relocation_info": {
      "target_airport_queue_id": "target_airport",
      "taximeter_tariffs": ["econom"]
    }
  }'::JSONB
),
(
  'udid7',
  'old_session_id7',
  'filtered_by_forbidden_reason',

  'dbid7_uuid7',
  'ekb',
  '2021-06-04T13:37:02.08513+00:00',
  NULL
),
(
  'udid8',
  'old_session_id8',
  'entered_on_order_wrong_client',

  'dbid8_uuid8',
  'ekb',
  '2021-06-04T13:06:02.08513+00:00',
  NULL
);

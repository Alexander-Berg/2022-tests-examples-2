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
  'udid3',
  'old_session_id3',
  'relocate_offer_created',

  'dbid_uuid3',
  'ekb',
  NOW() - INTERVAL '15 minutes',
  '{
    "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["vip"]
    }
  }'::JSONB
),
(
  'udid4',
  'old_session_id4',
  'relocate_offer_created',

  'dbid_uuid4',
  'ekb',
  NOW() - INTERVAL '15 minutes',
  '{
    "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["vip"]
    }
  }'::JSONB
),
(
  'udid5',
  'old_session_id5',
  'relocate_offer_created',

  'dbid_uuid5',
  'ekb',
  NOW() - INTERVAL '15 minutes',
  '{
    "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["vip"]
    }
  }'::JSONB
),
(
  'udid6',
  'old_session_id6',
  'relocate_offer_created',

  'dbid_uuid6',
  'ekb',
  NOW() - INTERVAL '15 minutes',
  '{
    "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["vip"]
    }
  }'::JSONB
)

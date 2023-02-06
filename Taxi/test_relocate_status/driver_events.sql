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
  'udid4',
  'session_id4',
  'relocate_offer_created',

  'dbid_uuid4',
  'svo',
  NOW(),
  '{
    "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom"]
    }
  }'::JSONB
),
(
  'udid5',
  'session_id5',
  'relocate_offer_created',

  'dbid_uuid5',
  'svo',
  NOW(),
  '{
    "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom"]
    }
  }'::JSONB
),
(
  'udid8',
  'session_id8',
  'relocate_offer_created',

  'dbid_uuid8',
  'svo',
  NOW(),
  '{
    "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom"]
    }
  }'::JSONB
),
(
  'udid9',
  'session_id9',
  'relocate_offer_created',

  'dbid_uuid9',
  'svo',
  NOW(),
  '{
    "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom"]
    }
  }'::JSONB
),
(
  'udid10',
  'session_id10',
  'relocate_offer_created',

  'dbid_uuid10',
  'svo',
  NOW(),
  '{
    "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom"]
    }
  }'::JSONB
);

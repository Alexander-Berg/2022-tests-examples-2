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
  'udid1',
  'old_session_id1',
  'relocate_offer_created',

  'dbid_uuid1',
  'ekb',
  NOW(),
  '{
    "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom", "comfortplus"]
    }
  }'::JSONB
),
(
    'udid2',
    'old_session_id2',
    'relocate_offer_created',

    'dbid_uuid2',
    'svo',
    NOW(),
    '{
      "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom", "comfortplus"]
      }
    }'::JSONB
),
(
    'udid8',
    'old_session_id8',
    'relocate_offer_created',

    'dbid_uuid8',
    'svo',
    NOW(),
    '{
      "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom", "comfortplus"]
      }
    }'::JSONB
),
(
    'udid9',
    'old_session_id9',
    'relocate_offer_created',

    'dbid_uuid9',
    'svo',
    NOW(),
    '{
      "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom", "comfortplus"]
      }
    }'::JSONB
);

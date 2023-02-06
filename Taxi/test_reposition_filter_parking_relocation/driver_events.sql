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
  'session_dbid_uuid1',
  'relocate_offer_created',

  'dbid_uuid1',
  'ekb',
  NOW() - INTERVAL '1 minutes',
  '{
    "relocation_info": {
      "target_airport_queue_id": "ekb",
      "taximeter_tariffs": ["econom", "business"]
    }
  }'::JSONB
),
(
  'udid6',
  'session_dbid_uuid6',
  'relocate_offer_created',

  'dbid_uuid6',
  'ekb',
  NOW() - INTERVAL '1 minutes',
  '{
    "relocation_info": {
      "target_airport_queue_id": "ekb",
      "taximeter_tariffs": ["econom", "business"]
    }
  }'::JSONB
),
(
  'udid7',
  'session_dbid_uuid7',
  'relocate_offer_created',

  'dbid_uuid7',
  'ekb',
  NOW() - INTERVAL '1 minutes',
  '{
    "relocation_info": {
      "target_airport_queue_id": "ekb",
      "taximeter_tariffs": ["econom", "business"]
    }
  }'::JSONB
);

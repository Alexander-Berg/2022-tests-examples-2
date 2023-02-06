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
  'udid6',
  'old_session_id6',
  'relocate_offer_created',

  'dbid_uuid6',
  -- check that airport_id and details will be changed
  'svo',
  NOW(),
  '{
    "relocation_info": {
        "target_airport_queue_id": "random_airport_id",
        "taximeter_tariffs": ["vip"]
    }
  }'::JSONB
);

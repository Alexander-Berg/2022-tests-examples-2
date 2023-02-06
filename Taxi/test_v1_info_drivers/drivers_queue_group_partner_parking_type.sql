INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,
  state,
  reason,
  entered,
  heartbeated,
  updated,
  queued,
  class_queued,
  airport,
  areas,
  classes,
  taximeter_tariffs,
  details
)
VALUES
  (
    'dbid_uuid0',
    'entered',
    'old_mode',
    NOW(),        -- entered
    NOW(),        -- heartbeated
    NOW(),        -- updated
    NULL,         -- queued
    NULL,
    'ekb',
    ARRAY[ 'notification' ] :: dispatch_airport.area_t[],
    ARRAY[ 'econom', 'comfortplus' ] :: text[],
    ARRAY[ 'econom', 'comfortplus' ] :: text[],
    '{"session_id": "session_id_0", "lon": 1, "lat": 1}' :: JSONB
  ),
  (
    'dbid_uuid1',
    'entered',
    'old_mode',
    NOW(),        -- entered
    NOW(),        -- heartbeated
    NOW(),        -- updated
    NULL,         -- queued
    NULL,
    'ekb',
    ARRAY[ 'notification', 'waiting', 'main' ] :: dispatch_airport.area_t[],
    ARRAY[ 'econom', 'comfortplus' ] :: text[],
    ARRAY[ 'econom', 'comfortplus' ] :: text[],
    '{"session_id": "session_id_1", "lon": 1, "lat": 1}' :: JSONB
  );

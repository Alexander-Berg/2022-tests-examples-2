INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id, state, reason, entered,
  heartbeated, updated, queued, class_queued, airport,
  areas, classes, taximeter_tariffs,
  details
)
VALUES
  (
    'dbid_uuid3', 'queued', 'old_mode',
    NOW(), NOW(), NOW(), NOW(), jsonb_build_object('econom', NOW()), 'ekb',
    ARRAY[ 'notification', 'main', 'waiting' ] :: dispatch_airport.area_t[],
    ARRAY[ 'econom' ] :: text[], ARRAY[ 'econom' ] :: text[],
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}' :: JSONB
  );

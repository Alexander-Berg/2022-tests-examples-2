INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id, state, reason, car_number, entered,
  heartbeated, updated, queued, class_queued, airport,
  areas, classes, taximeter_tariffs,
  details, reposition_session_id
)
VALUES
  (
    'dbid_uuid1', 'entered', 'on_action', 'ХЕ35377',
    NOW(), NOW(), NOW(), NOW(), jsonb_build_object('econom', NOW()), 'ekb',
    ARRAY[ 'notification', 'main', 'waiting' ] :: dispatch_airport.area_t[],
    ARRAY[ 'econom' ] :: text[], ARRAY[ 'econom' ] :: text[],
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}' :: JSONB, NULL
  ),
  (
    'dbid_uuid2', 'entered', 'on_action', 'У555УУ55',
    NOW(), NOW(), NOW(), NOW(), jsonb_build_object('econom', NOW()), 'ekb',
    ARRAY[ 'notification', 'main', 'waiting' ] :: dispatch_airport.area_t[],
    ARRAY[ 'econom' ] :: text[], ARRAY[ 'econom' ] :: text[],
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}' :: JSONB, NULL
  ),
  (
    'dbid_uuid3', 'entered', 'on_reposition', 'У555УУ55',
    NOW(), NOW(), NOW(), NOW(), jsonb_build_object('econom', NOW()), 'ekb',
    ARRAY[ 'notification', 'main'] :: dispatch_airport.area_t[],
    ARRAY[ 'econom' ] :: text[], ARRAY[ 'econom' ] :: text[],
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}' :: JSONB, 'dbid_uuid3_session'
  ),
  (
    'dbid_uuid4', 'queued', 'on_action', 'У555УУ55',
    NOW(), NOW(), NOW(), NOW(), jsonb_build_object('econom', NOW()), 'ekb',
    ARRAY[ 'notification', 'main', 'waiting' ] :: dispatch_airport.area_t[],
    ARRAY[ 'econom' ] :: text[], ARRAY[ 'econom' ] :: text[],
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}' :: JSONB, NULL
  );

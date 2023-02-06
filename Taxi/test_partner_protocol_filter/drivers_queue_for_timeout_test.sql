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
  input_order_id,
  reposition_session_id,
  details
)
VALUES
  (
    'dbid_uuid3', -- driver_id
    'entered',  -- state
    'on_reposition',  -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW(), -- queued
    jsonb_build_object('econom', NOW()), -- class_queued
    'ekb', -- airport
    ARRAY[ 'notification', 'main', 'waiting' ] :: dispatch_airport.area_t[], -- areas
    ARRAY[ 'econom' ] :: text[], -- classes
    ARRAY[ 'econom' ] :: text[], -- taximeter_tariffs
    NULL, -- input_order_id
    'reposition_session_3', -- reposition_session_id
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}' :: JSONB -- details
  ),
  (
    'dbid_uuid4', -- driver_id
    'entered',  -- state
    'on_action',  -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW(), -- queued
    jsonb_build_object('econom', NOW()), -- class_queued
    'ekb', -- airport
    ARRAY[ 'notification', 'main', 'waiting' ] :: dispatch_airport.area_t[], -- areas
    ARRAY[ 'econom' ] :: text[], -- classes
    ARRAY[ 'econom' ] :: text[], -- taximeter_tariffs
    'input_order_4', -- input_order_id
    NULL, -- reposition_session_id
    '{"session_id": "session_id_4", "lon": 1, "lat": 1}' :: JSONB -- details
  ),
  (
    'dbid_uuid5', -- driver_id
    'entered',  -- state
    'old_mode',  -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW(), -- queued
    jsonb_build_object('econom', NOW()), -- class_queued
    'ekb', -- airport
    ARRAY[ 'notification', 'main', 'waiting' ] :: dispatch_airport.area_t[], -- areas
    ARRAY[ 'econom' ] :: text[], -- classes
    ARRAY[ 'econom' ] :: text[], -- taximeter_tariffs
    NULL, -- input_order_id
    NULL, -- reposition_session_id
    '{"session_id": "session_id_5", "lon": 1, "lat": 1}' :: JSONB -- details
  );

INSERT INTO dispatch_airport.driver_events (
  udid,
  event_id,
  event_type,

  driver_id,
  airport_id,
  inserted_ts,
  details
) VALUES
--  no state started reposition with econom, comfort, but finished with only comfort
(
  'udid10',
  'old_session_id10',
  'relocate_offer_created',

  'driver_id10',
  'ekb',
  NOW() - INTERVAL '15 minutes',
  '{
    "relocation_info": {
      "target_airport_queue_id": "ekb",
      "taximeter_tariffs": ["econom", "business"]
    }
  }'::JSONB
),
--  no state started reposition with econom, but finished with econom, business
(
    'udid11',
    'old_session_id11',
    'relocate_offer_created',

    'driver_id11',
    'ekb',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom"]
      }
    }'::JSONB
),
--  entered started reposition with econom, comfort, but finished with only comfort
(
    'udid12',
    'old_session_id12',
    'relocate_offer_created',

    'driver_id12',
    'ekb',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom", "business"]
      }
    }'::JSONB
),
--  entered started reposition with econom, but finished with econom, business
(
    'udid13',
    'old_session_id13',
    'relocate_offer_created',

    'driver_id13',
    'ekb',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom"]
      }
    }'::JSONB
),
(
    'udid14',
    'old_session_id14',
    'relocate_offer_created',

    'driver_id14',
    'ekb',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom"]
      }
    }'::JSONB
),
(
    'udid15',
    'old_session_id15',
    'relocate_offer_created',

    'driver_id15',
    'ekb',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom"]
      }
    }'::JSONB
),
(
    'udid16',
    'very_old_session_id16',
    'relocate_offer_created',

    'driver_id16',
    'ekb',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "svo",
        "taximeter_tariffs": ["econom"]
      }
    }'::JSONB
),
(
    'udid18',
    'very_old_session_id18',
    'relocate_offer_created',

    'driver_id18',
    'svo',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom", "comfortplus"],
        "new_mode_tariffs": ["comfortplus"]
      }
    }'::JSONB
),
(
    'udid19',
    'very_old_session_id19',
    'relocate_offer_created',

    'driver_id19',
    'svo',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom", "comfortplus"],
        "new_mode_tariffs": ["econom"]
      }
    }'::JSONB
),
(
    'udid20',
    'very_old_session_id20',
    'relocate_offer_created',

    'driver_id20',
    'svo',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom", "comfortplus"],
        "new_mode_tariffs": []
      }
    }'::JSONB
),
(
    'udid21',
    'very_old_session_id21',
    'relocate_offer_created',

    'driver_id21',
    'svo',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom", "comfortplus"],
        "new_mode_tariffs": ["econom", "comfortplus"]
      }
    }'::JSONB
),
(
    'udid22',
    'very_old_session_id22',
    'relocate_offer_created',

    'driver_id22',
    'svo',
    NOW() - INTERVAL '15 minutes',
    '{
      "relocation_info": {
        "target_airport_queue_id": "ekb",
        "taximeter_tariffs": ["econom", "comfortplus"]
      }
    }'::JSONB
);

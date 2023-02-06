INSERT INTO eats_restapp_places.switching_on_requested (place_id, created_at, updated_at)
VALUES (42, NOW(), NOW())

ON CONFLICT (place_id)
DO
UPDATE SET updated_at = NOW()

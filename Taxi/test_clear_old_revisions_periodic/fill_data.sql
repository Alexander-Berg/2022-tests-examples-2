INSERT INTO eats_restapp_menu.distlock_periodic_updates (task_id, updated)
VALUES ('clear-old-revisions-periodic', '2021-06-10T00:00:00Z');

INSERT INTO eats_restapp_menu.menu_content(place_id, menu_hash, menu_json)
VALUES
    (123, 'some_hash1', '{"categories":[], "items": []}'),
    (124, 'some_hash2', '{"categories":[], "items": []}'),
    (126, 'some_hash2', '{"categories":[], "items": []}'),
    (124, 'some_hash4', '{"categories":[], "items": []}'),
    (125, 'some_hash2', '{"categories":[], "items": []}'),
    (126, 'some_hash6', '{"categories":[], "items": []}'),
    (124, 'some_hash9', '{"categories":[], "items": []}'),
    (124, 'some_hash3', '{"categories":[], "items": []}');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, origin, status, menu_hash, created_at)
VALUES
    (123, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla1', 'user_generated', 'applied', 'some_hash1', NOW() - INTERVAL '28 hour'),
    (124, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla2', 'user_generated', 'applied', 'some_hash2', NOW() - INTERVAL '2 hour'),
    (123, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla3', 'user_generated', 'applied', 'some_hash1', NOW() - INTERVAL '30 hour'),
    (124, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla4', 'user_generated', 'applied', 'some_hash4', NOW() - INTERVAL '12 hour'),
    (125, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla5', 'user_generated', 'applied', 'some_hash2', NOW() - INTERVAL '7 hour'),
    (126, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla6', 'user_generated', 'applied', 'some_hash6', NOW() - INTERVAL '33 hour'),
    (126, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla7', 'user_generated', 'applied', 'some_hash2', NOW() - INTERVAL '25 hour'),
    (124, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla8', 'user_generated', 'applied', 'some_hash2', NOW() - INTERVAL '26 hour'),
    (124, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla9', 'user_generated', 'applied', 'some_hash9', NOW() - INTERVAL '25 hour'),
    (124, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla10', 'user_generated', 'applied', 'some_hash3', NOW() - INTERVAL '1 hour');

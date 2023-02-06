INSERT INTO checks.immobility (immobility_id, min_track_speed, position_threshold, _max_immobility_time) VALUES
(1701, 5, 100,  make_interval(secs=>120));

INSERT INTO settings.driver_ids SELECT 10000 + num, ('dbid777', CONCAT('uuid_', num))::db.driver_id FROM generate_series(1, 200) num;

INSERT INTO config.completion_bonuses(mode_id, period, image, tanker_key)
VALUES (1, '1h', 'image_1', 'tanker_key_1');

INSERT INTO settings.points
(point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
SELECT 20000 + num, 1, 10000 + num, '09-01-2018', 'dbid777_888_home', 'some home address', 'Postgresql', (3, 4)::db.geopoint, NULL FROM generate_series(1, 200) num;

INSERT INTO state.sessions (session_id, driver_id_id, active, point_id, start, "end", mode_id, destination_point)
SELECT 30000 + num, 10000 + num, TRUE, 20000 + num, '2017-10-18T07:38:00+0000', NULL, 1, (3, 4)::db.geopoint FROM generate_series(1, 200) num;

INSERT INTO state.checks (session_id, duration_id, arrival_id, immobility_id, checking, last_check, _immobility_check_data, immobility_last_check)
SELECT 30000 + num, NULL, NULL, 1701, NULL, '2017-10-18T07:33:00+0000', ((37.63168, 55.736567), '2017-10-18T07:33:00+0000', 0)::db._immobility_check_data, '2017-10-18T07:33:00+0000' FROM generate_series(1, 200) num;



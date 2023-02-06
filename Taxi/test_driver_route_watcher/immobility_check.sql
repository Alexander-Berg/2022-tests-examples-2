INSERT INTO checks.immobility (immobility_id, min_track_speed, position_threshold, _max_immobility_time) VALUES
(1701, 5, 100, make_interval(secs=>120));


INSERT INTO settings.points
(point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id) VALUES
(1401, 1, IdId('888', 'dbid777'), '09-01-2018', 'dbid777_888_home', 'some home address', 'Postgresql', (3, 4), NULL);

INSERT INTO state.sessions (session_id, driver_id_id, active, point_id, start, "end", mode_id, destination_point) VALUES
(1501, IdId('888', 'dbid777'), TRUE, 1401, '2017-10-18T07:38:00+0000', NULL, 1, (3, 4))
;


INSERT INTO state.checks (session_id, duration_id, arrival_id, immobility_id, checking, last_check, _immobility_check_data, immobility_last_check) VALUES
(1501, NULL, NULL, 1701, NULL, '2017-10-18T07:33:00+0000', ((37.63168, 55.736567), '2017-10-18T07:33:00+0000', 0), '2017-10-18T07:33:00+0000')
;


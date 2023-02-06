INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (3,'poi',True,100, 2000, 180000, ('ToPoint')::db.mode_type)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
  VALUES
  (101, 1, IdId('888','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (102, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (103, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL);

INSERT INTO settings.saved_points (saved_point_id, point_id) VALUES (4001, 101);

INSERT INTO state.sessions
  (session_id, active, point_id, start, "end", driver_id_id, mode_id, destination_point)
  VALUES
  (2003, True, 102, '2018-10-12T16:02:11.540859', NULL, IdId('uuid','dbid777'), 3, (3, 4)::db.geopoint);

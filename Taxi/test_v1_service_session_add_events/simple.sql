INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
  VALUES
  (2001, 1, IdId('uuid','dbid'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (30, 60)::db.geopoint, NULL)
  ;

INSERT INTO state.sessions(session_id, point_id, active, start, driver_id_id, mode_id, destination_point) VALUES (3001, 2001, true, '2017-11-19T16:47:54.721', IdId('uuid','dbid'), 1, (30, 60)::db.geopoint);

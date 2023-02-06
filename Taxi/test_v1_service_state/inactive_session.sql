INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,             updated,      name,          address,         city,  location)
VALUES
  (111,      3,       IdId('driverSS', '1488'), '09-01-2018', 'pg_point_10', 'some address', 'Test', (3, 5)::db.geopoint);

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        driver_id_id,             mode_id, destination_point)
VALUES
  (2011,       False,  105,      '2018-10-12T16:03:45.540859', IdId('driverSS', '1488'), 1,       (3, 5)::db.geopoint);

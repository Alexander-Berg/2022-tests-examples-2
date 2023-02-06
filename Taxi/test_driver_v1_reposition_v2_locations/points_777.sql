INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,             updated,                   name,          address,          city,   location)
VALUES
  (2001,     1,       IdId('driverSS', '1488'), '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (37.41389, 55.97194)::db.geopoint),
  (2002,     2,       IdId('driverSS', '1488'), '09-01-2018',              'poi_name_1',  'poi_address_1',  'city', (3, 4)::db.geopoint),
  (2003,     2,       IdId('driverSS', '1488'), '09-01-2018',              'poi_name_2',  'poi_address_2',  'city', (5, 6)::db.geopoint);

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
VALUES
  (1001,           2001),
  (1002,           2002),
  (1003,           2003);

INSERT INTO state.sessions
  (session_id, active, point_id, "start",               "end",                 driver_id_id,             completed, is_usage, mode_id, destination_point)
VALUES
  (1,          True,   2001,     '2017-10-15 18:15:46', '2017-10-15 18:15:46', IdId('driverSS', '1488'), True,      True,     1,       (37.41389, 55.97194)::db.geopoint),
  (2,          True,   2001,     '2017-10-14 18:15:46', '2017-10-15 18:15:46', IdId('driverSS', '1488'), True,      True,     1,       (37.41389, 55.97194)::db.geopoint),
  (3,          True,   2001,     '2017-10-14 18:13:46', '2017-10-15 18:15:46', IdId('driverSS', '1488'), True,      True,     1,       (37.41389, 55.97194)::db.geopoint);

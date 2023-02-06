INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location)
VALUES
  (2002, 3, IdId('driverSS', '1488'), '09-01-2018', 'poi_name_1', 'poi_address_1', 'city', (3, 4)::db.geopoint),
  (2003, 3, IdId('driverSS', '1488'), '09-01-2018', 'poi_name_2', 'poi_address_2', 'city', (5, 6)::db.geopoint)
  ;

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
VALUES
  (1002, 2002),
  (1003, 2003)
  ;

INSERT INTO state.sessions
  (active, point_id, start,  "end", driver_id_id, completed, is_usage, mode_id, destination_point)
VALUES
  (True, 2003, '2018-01-14 20:21:20', '2018-01-14 20:21:20', IdId('driverSS', '1488'), True, True, 3, (5, 6)::db.geopoint),
  (True, 2003, '2018-01-14 20:21:21', '2018-01-14 20:21:20', IdId('driverSS', '1488'), True, True, 3, (5, 6)::db.geopoint),
  (True, 2003, '2018-01-14 20:21:22', '2018-01-14 20:21:20', IdId('driverSS', '1488'), True, True, 3, (5, 6)::db.geopoint)
  ;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location)
  VALUES
  (2001, 1, IdId('driverSS','1488'), '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint),
  (2002, 2, IdId('driverSS','1488'), '09-01-2018', 'poi_name_1', 'poi_address_1', 'city', (3, 4)::db.geopoint),
  (2003, 2, IdId('driverSS','1488'), '09-01-2018', 'poi_name_2', 'poi_address_2', 'city', (5, 6)::db.geopoint);

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
  VALUES
  (1001, 2001),
  (1002, 2002),
  (1003, 2003);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location)
VALUES
  (2002, 3, IdId('888', 'dbid777'), '09-01-2018', 'poi_name_1', 'poi_address_1', 'city', (3, 4)::db.geopoint),
  (2003, 3, IdId('888', 'dbid777'), '09-01-2018', 'poi_name_2', 'poi_address_2', 'city', (5, 6)::db.geopoint),
  (2004, 3, IdId('driverSS2', '1488'), '09-01-2018', 'poi_name_2', 'poi_address_2', 'city', (5, 6)::db.geopoint)
  ;

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
VALUES
  (1002, 2002),
  (1003, 2003),
  (1004, 2004)
  ;

INSERT INTO state.sessions
  (session_id, active, point_id, start,  "end", driver_id_id, completed, is_usage, mode_id, destination_point)
VALUES
  (101, True, 2003, '2018-01-13 20:21:20', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (102, True, 2003, '2018-01-13 20:21:21', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (103, True, 2003, '2018-01-13 20:21:22', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (104, True, 2003, '2018-01-13 20:21:23', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (105, True, 2003, '2018-01-13 20:21:24', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (106, True, 2003, '2018-01-13 20:21:25', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (107, True, 2003, '2018-01-13 20:21:26', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (108, True, 2003, '2018-01-13 20:21:27', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (109, True, 2003, '2018-01-13 20:21:28', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (110, True, 2003, '2018-01-13 20:21:29', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (111, True, 2003, '2018-01-13 20:21:30', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (112, True, 2003, '2018-01-13 20:21:31', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (113, True, 2003, '2018-01-13 20:21:32', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (114, True, 2003, '2018-01-13 20:21:33', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (115, True, 2003, '2018-01-13 20:21:34', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (116, True, 2003, '2018-01-13 20:21:35', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (117, True, 2003, '2018-01-13 20:21:36', '2018-01-13 20:21:20', IdId('888', 'dbid777'), True, True, 3, (5, 6)::db.geopoint),
  (118, True, 2004, '2018-01-14 22:21:36', '2018-01-14 22:25:20', IdId('driverSS2', '1488'), True, True, 3, (5, 6)::db.geopoint)
  ;

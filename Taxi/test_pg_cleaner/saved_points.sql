INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (3,'poi',True,100, 2000, 180000, ('ToPoint')::db.mode_type);

INSERT INTO config.usage_rules
  (mode_id, change_interval)
VALUES
  (1, NULL),
  (3, interval '4 days');

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('888','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (102, 1, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (103, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (104, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (105, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL);

INSERT INTO settings.saved_points
  (saved_point_id, point_id, deleted, updated)
VALUES
  (4001, 101, False, '2018-10-16T16:03:11'), /* not deleted */
  (4002, 102, True,  '2018-10-16T16:03:11'), /* deleted in mode with no interval */
  (4003, 103, True,  '2018-10-14T16:03:11'), /* deleted in 2 days */
  (4004, 104, True,  '2018-10-10T16:03:11'), /* deleted in 6 days */
  (4005, 105, False, '2018-10-10T16:03:11'); /* not deleted in 6 days */

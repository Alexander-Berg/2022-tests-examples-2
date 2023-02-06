INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (1,'no_checks',True,100, 2000, 180000, ('ToPoint')::db.mode_type),
  (2,'only_day',True,100, 2000, 180000, ('ToPoint')::db.mode_type),
  (3,'only_week',True,100, 2000, 180000, ('ToPoint')::db.mode_type),
  (4,'both',True,100, 2000, 180000, ('ToPoint')::db.mode_type)
;

INSERT INTO config.usage_rules
  (mode_id, day_usage_limit, week_usage_limit)
VALUES
  (2, 1, NULL),
  (3, NULL, 1),
  (4, 1, 1)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (201, 2, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (301, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (401, 4, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL)
  ;

INSERT INTO state.archive_sessions
  (session_id, active, point_id, start, "end", driver_id_id, start_point, mode_id)
VALUES
  /* Today */
  (1101, True, 101, '2018-10-12T16:01:11.540859', '2018-10-16T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 1),
  (1201, True, 201, '2018-10-12T16:01:11.540859', '2018-10-16T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 2),
  (1301, True, 301, '2018-10-12T16:01:11.540859', '2018-10-16T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 3),
  (1401, True, 401, '2018-10-12T16:01:11.540859', '2018-10-16T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 4),
  /* Yesterday */
  (2101, True, 101, '2018-10-12T16:01:11.540859', '2018-10-15T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 1),
  (2201, True, 201, '2018-10-12T16:01:11.540859', '2018-10-15T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 2),
  (2301, True, 301, '2018-10-12T16:01:11.540859', '2018-10-15T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 3),
  (2401, True, 401, '2018-10-12T16:01:11.540859', '2018-10-15T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 4),
  /* Week ago */
  (3101, True, 101, '2018-10-12T16:01:11.540859', '2018-10-9T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 1),
  (3201, True, 201, '2018-10-12T16:01:11.540859', '2018-10-9T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 2),
  (3301, True, 301, '2018-10-12T16:01:11.540859', '2018-10-9T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 3),
  (3401, True, 401, '2018-10-12T16:01:11.540859', '2018-10-9T15:03:11.540859', IdId('uuid','dbid777'), (3, 4)::db.geopoint, 4)
  ;


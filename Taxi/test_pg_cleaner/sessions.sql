INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (3,'poi',True,100, 2000, 180000, ('ToPoint')::db.mode_type)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('888','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (102, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL);

INSERT INTO state.sessions
  (session_id, active, point_id, start, "end", driver_id_id, mode_id, destination_point)
VALUES
  (2001, True,  101, '2018-10-12T16:01:11.540859', '2018-10-12T16:03:11.540859', IdId('888','dbid777'), 1, (3, 4)::db.geopoint),
  (2002, True,  102, '2018-10-11T16:02:11.540859', '2018-10-11T16:03:11.540859', IdId('uuid','dbid777'), 3, (3, 4)::db.geopoint),
  (2003, True,  102, '2018-10-12T16:02:11.540859', NULL,                  IdId('uuid','dbid777'), 3, (3, 4)::db.geopoint),
  (2004, True,  102, '2018-10-12T15:00:00',        '2018-10-12T16:00:00', IdId('uuid','dbid777'), 3, (3, 4)::db.geopoint),
  (2005, False, 102, '2018-10-12T15:00:00',        '2018-10-12T17:00:00', IdId('uuid','dbid777'), 3, (3, 4)::db.geopoint),
  (2006, False, 102, '2018-10-12T15:00:00',        '2018-10-12T18:00:00', IdId('uuid','dbid777'), 3, (3, 4)::db.geopoint);

INSERT INTO state.events
  (session_id, event, occured_at)
VALUES
  (2001, 'OrderStarted', current_timestamp),
  (2003, 'OrderStarted', current_timestamp);

INSERT INTO state.sessions_rule_violations (session_id, violations, created_at)
VALUES
(2001, ROW('{}'::db.rule_violation[]), '2018-09-01 07:00:00'),
(2003, ROW('{}'::db.rule_violation[]), '2018-09-01 07:00:00');

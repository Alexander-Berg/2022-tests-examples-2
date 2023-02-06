INSERT INTO config.modes
  (mode_id, mode_name, offer_only, min_allowed_distance, max_allowed_distance, mode_type,                 work_modes)
VALUES
  (1,       'home',    FALSE,      2000,                 180000,               ('ToPoint')::db.mode_type, ARRAY['orders']);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,             updated,      name,         address,        city,         location,            offer_id)
VALUES
  (101,      1,       IdId('driverSS', '1488'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (102,      1,       IdId('driverSS', '1488'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (103,      1,       IdId('888', 'dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (104,      1,       IdId('888', 'dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL);

INSERT INTO config.usage_rules
  (mode_id, day_duration_limit_sum, week_duration_limit_sum)
VALUES
  (1,       '1 hour',               '3 hours');

INSERT INTO check_rules.duration
  (duration_id, _span)
VALUES
  (125,         '1 hour');

INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id, arrival_id, immobility_id, surge_arrival_id, submode_id)
VALUES
  (1,       1,       125,         NULL,       NULL,          NULL,             NULL);

INSERT INTO state.sessions
  (session_id, point_id, start, "end", active, mode_id, destination_point, driver_id_id, is_usage, session_deadline)
VALUES
  (101, 103, '2020-01-13T01:00:00.000000', '2020-01-13T01:30:00.000000', False, 1, (3, 4)::db.geopoint, IdId('888', 'dbid777'), TRUE, '2020-01-13T02:00:00.000000'),
  (102, 104, '2020-01-13T04:00:00.000000', NULL, True, 1, (3, 4)::db.geopoint, IdId('888', 'dbid777'), TRUE, NULL),
  (103, 101, '2020-01-12T01:00:00.000000', '2020-01-12T01:30:00.000000', False, 1, (3, 4)::db.geopoint, IdId('driverSS', '1488'), TRUE, '2020-01-12T02:00:00.000000'),
  (104, 102, '2020-01-13T04:00:00.000000', NULL, True, 1, (3, 4)::db.geopoint, IdId('driverSS', '1488'), TRUE, NULL);


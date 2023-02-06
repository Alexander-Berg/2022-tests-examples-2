INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,             updated,      name,         address,        city,         location)
VALUES
  (101,      1,       IdId('uuid', 'dbid777'),  '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint),
  (102,      1,       IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint)
;

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        driver_id_id,             mode_id, destination_point,   is_usage, session_deadline)
VALUES
  (2001,       True,   101,      '2018-11-26T20:11:00.540859', IdId('uuid', 'dbid777'),  1,       (3, 4)::db.geopoint, True, '2018-11-26T:22:11:00.540859'),
  (2002,       False,  101,      '2018-10-11T21:01:11.540859', IdId('uuid1', 'dbid777'), 1,       (3, 4)::db.geopoint, False, NULL)
;

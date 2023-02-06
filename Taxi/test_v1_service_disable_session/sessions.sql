INSERT INTO settings.points
(point_id, mode_id, driver_id_id,             updated,      name,         address,        city,         location)
VALUES
    (101,      1,       IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_3', 'some address', 'Postgresql', (30, 60)::db.geopoint),
    (102,      3,       IdId('uuid2', 'dbid777'), '09-01-2018', 'pg_point_3', 'some address', 'Postgresql', (30, 60)::db.geopoint)
;

INSERT INTO state.sessions
(session_id, active, point_id, start,                         "end",                         driver_id_id,              mode_id, destination_point)
VALUES
    (1001,       True,   101,      '2018-10-11T18:00:11.540859', NULL,                         IdId('uuid1', 'dbid777'),  1,       (30, 60)::db.geopoint),
    (1002,       True,   102,      '2018-10-11T18:00:11.540859', NULL,                         IdId('uuid2', 'dbid777'),  3,       (30, 60)::db.geopoint),
    (1003,       False,  102,      '2018-10-11T18:00:11.540859', NULL,                         IdId('driverSS', '1488'),  3,       (30, 60)::db.geopoint),
    (1004,       False,  102,      '2018-10-11T18:00:11.540859', '2018-10-11T19:00:11.540859', IdId('driverSS2', '1488'), 3,       (30, 60)::db.geopoint)
;

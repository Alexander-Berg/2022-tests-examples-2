INSERT INTO settings.points(point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
(101, 1, IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_3', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
(102, 1, IdId('uuid2', 'dbid777'), '09-01-2018', 'pg_point_4', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL);

INSERT INTO state.sessions(session_id, active, point_id, start, driver_id_id, mode_id, destination_point)
VALUES (1001, True, 101, '2018-10-11T16:01:11.540859', IdId('uuid1', 'dbid777'), 1, (3, 4)::db.geopoint),
       (1002, True, 102, '2018-10-12T15:40:11.540859', IdId('uuid2', 'dbid777'), 1, (3, 4)::db.geopoint);

INSERT INTO state.events(session_id, event, occured_at)
VALUES (1001, 'Arrived', '2018-10-11T16:06:11.540859'),
       (1002, 'OrderFinished', '2018-10-11T16:06:11.540859');

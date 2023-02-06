INSERT INTO  state.offers
  (offer_id, valid_until,                  image_id,      description,    used,  origin)
VALUES
  (1001,     '2018-11-26T13:00:00.000000', 'image_id_1', 'description_1', False, ('reposition-relocator')::db.offer_origin),
  (1002,     '2018-11-26T12:45:00.000000', 'image_id_2', 'description_2', True,  ('reposition-relocator')::db.offer_origin),
  (1003,     '2018-11-26T12:00:00.000000', 'image_id_3', 'description_3', True,  ('reposition-relocator')::db.offer_origin),
  (1004,     '2018-11-26T11:59:59.999999', 'image_id_4', 'description_4', False, ('reposition-relocator')::db.offer_origin),
  (1005,     '2018-11-26T14:00:00.000000', 'image_id_5', 'description_5', False, ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('888', 'dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (102, 3, IdId('uuid', 'dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (103, 3, IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_3', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (104, 3, IdId('uuid2', 'dbid777'), '09-01-2018', 'pg_point_4', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (105, 3, IdId('uuid3', 'dbid777'), '09-01-2018', 'pg_point_4', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (106, 3, IdId('uuid3', 'dbid777'), '09-01-2018', 'pg_point_5', 'some address', 'Postgresql', (37.1946401739712, 55.478983901730004)::db.geopoint, 1001),
  (107, 3, IdId('uuid', 'dbid777'), '09-01-2018', 'pg_point_6', 'some address', 'Spb', (30.15629725, 59.89538895)::db.geopoint, 1002),
  (108, 3, IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_7', 'some address', 'Moscow', (37.1946401739712, 55.478983901730004)::db.geopoint, 1003),
  (109, 3, IdId('uuid2', 'dbid777'), '09-01-2018', 'pg_point_8', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1004),
  (110, 3, IdId('uuid2', 'dbid777'), '09-01-2018', 'pg_point_9', 'some address', 'Moscow', (37.1946401739712, 55.478983901730004)::db.geopoint, 1005);

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        "end",                        driver_id_id,             mode_id, submode_id, destination_point,                   session_deadline,            start_router_info)
VALUES
  (2001,       True,   101,      '2018-10-11T16:01:11.540859', '2018-10-11T16:02:11.540859', IdId('888', 'dbid777'),   1,       NULL,       (3,         4)::db.geopoint,         NULL,                         NULL),
  (2002,       True,   102,      '2018-10-12T15:40:11.540859', '2018-10-12T16:04:11.540859', IdId('uuid', 'dbid777'),  3,       NULL,       (3,         4)::db.geopoint,         NULL,                         NULL),
  (2003,       True,   102,      '2018-10-12T16:05:11.540859', NULL,                         IdId('uuid', 'dbid777'),  3,       NULL,       (37.617664, 55.752121)::db.geopoint, '2018-10-12T17:05:11.540859', (300, 1000)::db.router_info),
  (2004,       True,   103,      '2018-10-12T16:05:11.540859', NULL,                         IdId('uuid1', 'dbid777'), 3,       NULL,       (3,         4)::db.geopoint,         '2018-10-12T16:03:11.000000', NULL),
  (2005,       True,   104,      '2018-10-12T16:05:11.540859', NULL,                         IdId('uuid2', 'dbid777'), 3,       NULL,       (3,         4)::db.geopoint,         '2018-10-12T16:05:00.000000', NULL),
  (2006,       True,   105,      '2018-10-12T16:05:11.540859', NULL,                         IdId('uuid3', 'dbid777'), 3,       301,        (3,         4)::db.geopoint,         '2018-10-12T16:05:00.000000', NULL),
  (2007,       True,   105,      '2018-10-12T16:03:11.540859', '2018-10-12T16:04:00.000000', IdId('uuid', 'dbid777'),  3,       301,        (3,         4)::db.geopoint,         NULL,                         NULL),
  (2008,       True,   101,      '2018-10-12T15:59:00.540859', '2018-10-12T16:04:11.540859', IdId('888', 'dbid777'),   1,       NULL,       (3,         4)::db.geopoint,         NULL,                         NULL),
  (2009,       True,   102,      '2018-10-12T16:03:45.540859', '2018-10-12T16:04:45.540859', IdId('uuid', 'dbid777'),  3,       NULL,       (3,         4)::db.geopoint,         NULL,                         NULL)
;

INSERT INTO state.check_rules
  (session_id, duration_id, arrival_id, immobility_id)
VALUES
  (2003, 1, 1, 1),
  (2004, 2, 1, 1),
  (2005, 3, 1, 1),
  (2006, 3, 1, 1);

INSERT INTO state.events
  (session_id, event, occured_at)
VALUES
  (2003, 'Arrived', '2018-10-11T16:06:11.540859');

INSERT INTO check_rules.duration
  (duration_id, due)
VALUES
  (1, current_timestamp),
  (2, current_timestamp),
  (3, current_timestamp),
  (4, current_timestamp),
  (5, current_timestamp),
  (6, current_timestamp),
  (7, current_timestamp),
  (8, current_timestamp),
  (9, current_timestamp),
  (10, current_timestamp);

INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id)
VALUES
  (1, 1, 4);


INSERT INTO  state.offers
  (offer_id, valid_until,                             due_id, image_id, description, origin)
VALUES
  (1001,     current_timestamp - ('1 day')::interval, 1,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1002,     current_timestamp - ('1 day')::interval, 2,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1003,     current_timestamp - ('1 day')::interval, 3,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1004,     current_timestamp + ('1 day')::interval, 5,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1005,     current_timestamp - ('1 day')::interval, 7,      '',       '',          ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('888','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1001),
  (102, 1, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1002),
  (103, 1, IdId('uuid2','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1003);

INSERT INTO state.archive_sessions
  (session_id, active, point_id, start, "end", driver_id_id, start_point, mode_id)
VALUES
  (2001, True, 101, '2018-10-12T16:01:11.540859', '2018-10-12T16:03:11.540859', IdId('888','dbid777'), (3, 4)::db.geopoint, 1);

INSERT INTO state.sessions
  (session_id, active, point_id, start, "end", driver_id_id, mode_id, destination_point)
VALUES
  (2002, True, 101, '2018-10-12T16:01:11.540859', '2018-10-12T16:03:11.540859', IdId('888','dbid777'), 1, (3, 4)::db.geopoint),
  (2003, True, 102, '2018-10-12T16:01:11.540859', '2018-10-12T16:03:11.540859', IdId('uuid','dbid777'), 1, (3, 4)::db.geopoint),
  (2004, True, 103, '2018-10-12T16:01:11.540859', '2018-10-12T16:03:11.540859', IdId('uuid2','dbid777'), 1, (3, 4)::db.geopoint);

INSERT INTO state.sessions_to_reposition_watcher
  (session_id, is_stop_action, duration_id, created_at)
VALUES
  (2002,       FALSE,          NULL,        NOW()),
  (2003,       FALSE,          4,           NOW()),
  (2004,       FALSE,          8,           NOW())
;

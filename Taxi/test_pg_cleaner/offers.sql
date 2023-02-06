INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (3,'poi',True,100, 2000, 180000, ('ToPoint')::db.mode_type)
;

INSERT INTO check_rules.duration
  (duration_id, due)
VALUES
  (1, current_timestamp);

INSERT INTO state.offers
  (offer_id, valid_until,                             due_id, image_id, description, origin)
VALUES
  (1001,     current_timestamp - ('1 day')::interval, 1,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1002,     current_timestamp - ('1 day')::interval, 1,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1003,     current_timestamp - ('1 day')::interval, 1,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1004,     current_timestamp + ('1 day')::interval, 1,      '',       '',          ('reposition-relocator')::db.offer_origin),
  (1005,     current_timestamp - ('1 day')::interval, 1,      '',       '',          ('reposition-relocator')::db.offer_origin);

INSERT INTO state.offers_metadata
  (offer_id, airport_queue_id, classes)
VALUES
  (1003,     'svo',            ARRAY['econom', 'business']),
  (1005,     'dme',            ARRAY['vip'])
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('888','dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1001),
  (102, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1002),
  (103, 3, IdId('uuid','dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1003);

INSERT INTO state.archive_sessions
  (session_id, active, point_id, start, "end", driver_id_id, start_point, mode_id)
VALUES
  (2001, True, 101, '2018-10-12T16:01:11.540859', '2018-10-12T16:03:11.540859', IdId('888','dbid777'), (3, 4)::db.geopoint, 1);

INSERT INTO state.sessions
  (session_id, active, point_id, start, "end", driver_id_id, mode_id, destination_point)
VALUES
  (2002, True, 102, '2018-10-12T16:01:11.540859', '2018-10-12T16:03:11.540859', IdId('uuid','dbid777'), 1, (3, 4)::db.geopoint);

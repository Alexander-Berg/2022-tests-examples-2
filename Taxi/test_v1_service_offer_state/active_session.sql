INSERT INTO  state.offers
  (offer_id, valid_until,                  image_id,      description,    used,  origin)
VALUES
  (1001,     '2018-11-26T13:00:00.000000', 'image_id_1', 'description_1', False, ('reposition-relocator')::db.offer_origin),
  (1002,     '2018-11-26T13:00:00.000000', 'image_id_1', 'description_1', False, ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('888', 'dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1001),
  (102, 1, IdId('888', 'dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1002);

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        "end",                        driver_id_id,             mode_id, submode_id, destination_point,   session_deadline)
VALUES
  (2001,       False,   101,      '2018-10-11T16:01:11.540859', NULL, IdId('888', 'dbid777'),   1,       NULL,       (3, 4)::db.geopoint, NULL)
;

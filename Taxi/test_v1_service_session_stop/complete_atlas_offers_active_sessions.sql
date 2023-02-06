INSERT INTO state.offers
  (offer_id, valid_until,           image_id, description,   completed_tags,             origin)
VALUES
  (1001,     '2018-10-16T18:18:46', 'image',  'description', ARRAY['offer_session_tag'], ('reposition-atlas')::db.offer_origin),
  (1002,     '2018-10-16T18:18:46', 'image',  'description', ARRAY['offer_session_tag'], ('reposition-atlas')::db.offer_origin)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,              updated,      name,         address,        city,         location,           offer_id)
VALUES
  (1001,     1,       IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1001),
  (1002,     1,       IdId('uuid2', 'dbid777'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1002)
;

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        driver_id_id,             mode_id, destination_point)
VALUES
  (1001,       True,   1001,     '2018-10-11T16:01:11.540859', IdId('uuid1', 'dbid777'), 1,       (3, 4)::db.geopoint),
  (1002,       True,   1002,     '2018-10-12T15:40:11.540859', IdId('uuid2', 'dbid777'), 1,       (3, 4)::db.geopoint)
;

INSERT INTO state.events
  (session_id, event,           occured_at)
VALUES
  (1001,      'Arrived',       '2018-10-11T16:06:11.540859'),
  (1002,      'OrderFinished', '2018-10-11T16:06:11.540859')
;

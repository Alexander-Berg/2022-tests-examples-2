INSERT INTO state.offers
  (offer_id, valid_until,           image_id, description,   completed_tags,             origin)
VALUES
  (1001,     '2018-10-16T18:18:46', 'image',  'description', ARRAY['offer_session_tag'], ('reposition-relocator')::db.offer_origin)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,             updated,      name,         address,        city,         location,              offer_id)
VALUES
  (101,      1,       IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_3', 'some address', 'Postgresql', (30, 60)::db.geopoint, 1001)
;

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        driver_id_id,             mode_id, destination_point)
VALUES
  (1001,       True,   101,      '2018-10-11T18:00:11.540859', IdId('uuid1', 'dbid777'), 1,       (30, 60)::db.geopoint)
;

INSERT INTO state.checks
  (session_id, duration_id, arrival_id)
VALUES
  (1001,       1,           1)
;

INSERT INTO state.offers
  (offer_id, valid_until,           image_id, description,   completed_tags,             origin)
VALUES
  (1003,     '2018-10-16T18:18:46', 'image',  'description', ARRAY['offer_session_tag'], ('reposition-relocator')::db.offer_origin)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,              updated,      name,         address,        city,         location,           offer_id)
VALUES
  (1003,     1,       IdId('uuid1', 'dbid777'), '09-01-2018', 'pg_point_3', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1003)
;

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        driver_id_id,             mode_id, destination_point)
VALUES
  (1003,       True,   1003,     '2018-10-12T15:40:11.540859', IdId('uuid3', 'dbid777'), 1,       (3, 4)::db.geopoint)
;

INSERT INTO state.events
  (session_id, event,           occured_at)
VALUES
  (1003,      'Immobility',    '2018-10-11T16:06:11.540859'),
  (1003,      'OrderFinished', '2018-10-11T16:08:11.540859')
;

INSERT INTO state.offers
  (offer_id, valid_until, image_id, description, session_tags, origin)
VALUES
  (1001, '2017-10-16T18:18:46', 'image', 'description', ARRAY['offer_session_tag'], ('reposition-relocator')::db.offer_origin),
  (1002, '2017-10-16T18:18:46', 'image', 'description', ARRAY['offer_session_tag'], ('reposition-atlas')::db.offer_origin)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (1001, 3, IdId('driverSS2', '1488'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (37.617664, 55.752121)::db.geopoint, 1001),
  (1002, 3, IdId('driverSS2', '1488'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (37.617664, 55.752121)::db.geopoint, 1002)
;

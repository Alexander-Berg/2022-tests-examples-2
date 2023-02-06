INSERT INTO check_rules.duration
  (duration_id, due)
VALUES
  (1, NOW() + INTERVAL '1 day');

INSERT INTO state.offers
  (offer_id, valid_until,                due_id, image_id, description, created,               origin)
VALUES
  (1,        '2018-09-10T11:00:00+0300', 1,      'icon',   'some text', '09-01-2018T20:20:00', ('reposition-relocator')::db.offer_origin),
  (2,        '2018-08-01T11:00:00+0300', 1,      'icon',   'some text', '09-01-2018T20:20:00', ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (1, 1, IdId('pg_driver','pg_park'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (30, 60)::db.geopoint, NULL),
  (2, 3, IdId('pg_driver','pg_park'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (30, 60)::db.geopoint, 1),
  (3, 3, IdId('pg_driver','pg_park'), '09-01-2018', 'pg_point_expired', 'some address', 'Postgresql', (30, 60)::db.geopoint, 2);

INSERT INTO config.usage_rules
  (mode_id,change_interval)
VALUES
  (1, INTERVAL '4 day');

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
VALUES
  (1, 1);

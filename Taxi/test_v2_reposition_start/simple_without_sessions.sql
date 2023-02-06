INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type,                 work_modes)
VALUES
  (3,       'poi',     False,      1000,         2000,                 180000,               ('ToPoint')::db.mode_type, ARRAY['orders']);

INSERT INTO config.submodes
  (submode_id, submode_name, mode_id, is_default)
VALUES
  (1, 'fast', 3, true),
  (2, 'medium', 3, false),
  (3, 'slow', 3, false)
;

INSERT INTO check_rules.duration
  (duration_id, due)
VALUES
  (1, '2017-10-16T18:18:46'), /* Time mock + 1 day */
  (2, '2017-10-17T18:18:46')  /* Time mock + 2 days */
;

INSERT INTO check_rules.arrival
  (arrival_id, _eta, distance)
VALUES
  (1, make_interval(secs=>123), 100),
  (2, make_interval(secs=>300), 200)
;

INSERT INTO check_rules.immobility
  (immobility_id, min_track_speed, position_threshold, _max_immobility_time)
VALUES
  (1, 11, 12, make_interval(secs=>13)),
  (2, 10, 10, make_interval(secs=>10))
;

INSERT INTO check_rules.surge_arrival
  (surge_arrival_id, time_coeff, surge_arrival_coef, min_arrival_surge, min_arrival_eta)
VALUES
  (1, 1.2, 0.9, 1.1, make_interval(secs => 50));

INSERT INTO state.offers
  (offer_id, created,               valid_until,           due_id, image_id, description,   origin)
VALUES
  (1,        '2017-10-16T14:18:46', '2017-10-16T18:18:46', 1,      'image',  'description', ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 1, IdId('driverSS', '1488'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (102, 3, IdId('driverSS', '1488'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1);

INSERT INTO config.usage_rules
  (mode_id, change_interval)
VALUES
  (1, interval '4 day');

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
VALUES
  (1, 101),
  (2, 102);

INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id, arrival_id, immobility_id, surge_arrival_id, submode_id)
VALUES
  (1, 1, 1, 1, 1, 1, NULL),
  (1, 1, 2, 2, 2, NULL, 1),
  (3, 1, 1, 1, 1, 1, NULL);

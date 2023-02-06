INSERT INTO config.modes
  (mode_id, mode_name,    offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type,                 work_modes)
VALUES
  (3,       'poi',        False,      NULL,         2000,                 180000,               ('ToPoint')::db.mode_type, ARRAY['orders']),
  (4,       'SuperSurge', True,       100,          2000,                 180000,               ('ToPoint')::db.mode_type, ARRAY['orders']);

INSERT INTO check_rules.duration
  (duration_id, due)
VALUES
  (1,           '2017-10-16T18:18:46');

INSERT INTO state.offers
  (offer_id, created,               valid_until,           due_id, image_id, description,   origin)
VALUES
  (1,        '2017-10-16T14:18:46', '2017-10-16T18:18:46', 1,      'image',  'description', ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101, 3, IdId('driverSS', '1488'), '09-01-2018', 'pg_point_2', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL),
  (102, 4, IdId('driverSS', '1488'), '09-01-2018', 'pg_point_3', 'some address', 'Postgresql', (3, 4)::db.geopoint, 1);

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
VALUES
  (1, 101);

INSERT INTO check_rules.arrival
  (arrival_id, _eta, distance)
VALUES
  (1, make_interval(secs=>123), 100);

INSERT INTO check_rules.immobility
  (immobility_id, min_track_speed, position_threshold, _max_immobility_time)
VALUES
  (1, 11, 12, make_interval(secs=>13));

INSERT INTO check_rules.transporting_arrival
  (transporting_arrival_id)
VALUES
  (1);

INSERT INTO check_rules.antisurge_arrival
  (antisurge_arrival_id, coef_surge, min_dest_surge, min_ride_time)
VALUES
  (1, 1, 1.4, make_interval(secs => 50));

INSERT INTO check_rules.surge_arrival
  (surge_arrival_id, time_coeff, surge_arrival_coef, min_arrival_surge, min_arrival_eta)
VALUES
  (1, 1.2, 0.9, 1.1, make_interval(secs => 50));

INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id, arrival_id, immobility_id, surge_arrival_id, transporting_arrival_id, antisurge_arrival_id)
VALUES
  (1, 1, 1, 1, 1, 1, 1, NULL),
  (3, 1, 1, 1, 1, 1, 1, 1);

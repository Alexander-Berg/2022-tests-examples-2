INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (1488,    'surge',   True,       100,          2000,                 180000,               ('ToPoint')::db.mode_type);


INSERT INTO settings.driver_ids
  (driver_id_id, driver_id)
VALUES
  (4001,         ('dbid777','d1')),
  (4002,         ('dbid777','d2')),
  (4003,         ('dbid777','d3')),
  (4004,         ('dbid777','d4')),
  (4005,         ('dbid777','d5')),
  (4006,         ('dbid777','d6'));

INSERT INTO  state.offers
  (offer_id, created,                      valid_until,                  image_id,    description,     used,  origin)
VALUES
  (1,    '2018-11-26T12:45:00.000000', '2018-11-26T13:00:00.000000', 'image_id_1', 'description_1', False, ('reposition-relocator')::db.offer_origin),
  (2,    '2018-11-26T12:30:00.000000', '2018-11-26T12:45:00.000000', 'image_id_2', 'description_2', True,  ('reposition-relocator')::db.offer_origin),
  (3,    '2018-11-26T11:45:00.000000', '2018-11-26T12:00:00.000000', 'image_id_3', 'description_3', True,  ('reposition-relocator')::db.offer_origin),
  (4,    '2018-11-26T11:43:59.999999', '2018-11-26T11:59:59.999999', 'image_id_4', 'description_4', False, ('reposition-relocator')::db.offer_origin),
  (5,    '2018-11-26T13:45:00.000000', '2018-11-26T14:00:00.000000', 'image_id_5', 'description_5', False, ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated,                   name,          address,          city,   location,            offer_id)
VALUES
  (1001,     1,       4001,         '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint, 1),
  (1002,     1,       4002,         '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint, 4),
  (1003,     1488,    4003,         '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint, 3),
  (1007,     1,       4004,         '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint, 2),
  (1008,     1,       4005,         '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint, 3),
  (1009,     1,       4006,         '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint, NULL);

INSERT INTO state.sessions
  (point_id, active, start,                     "end",                     completed, revision, driver_id_id, mode_id, destination_point)
VALUES
  (1001,     True,   '2017-11-19T16:47:54.721', NULL,                      False,     2,        4001,         1,       (1, 2)::db.geopoint),
  (1002,     False,  '2017-11-19T16:42:54.721', NULL,                      False,     3,        4002,         1,       (1, 2)::db.geopoint),
  (1003,     True,   '2017-11-19T16:37:54.721', '2017-11-19T16:57:54.721', True,      4,        4003,         1488,    (1, 2)::db.geopoint),
  (1007,     True,   '2017-11-19T16:32:54.721', NULL,                      False,     8,        4004,         1,       (1, 2)::db.geopoint),
  (1008,     True,   '2017-11-19T16:32:54.721', NULL,                      False,     9,        4005,         1,       (1, 2)::db.geopoint),
  (1009,     True,   '2017-11-19T16:32:54.721', NULL,                      False,     10,       4006,         1,       (1, 2)::db.geopoint);

INSERT INTO state.offers_metadata
  (offer_id, airport_queue_id, is_dispatch_airport_pin)
VALUES
  (1,        'q1', False),
  (2,        'q2', False),
  (3,        'q1', True),
  (4,        'q3', False);

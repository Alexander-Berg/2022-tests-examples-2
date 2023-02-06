INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (1488,'surge', True, 100, 2000, 180000, ('ToPoint')::db.mode_type);

INSERT INTO config.completion_bonuses
  (mode_id, period, image, tanker_key)
VALUES
  (1488, interval '10 minutes', '', '');

INSERT INTO settings.driver_ids
  (driver_id_id, driver_id)
VALUES
  (4001, ('dbid777','d1')),
  (4002, ('dbid777','d2')),
  (4003, ('dbid777','d3')),
  (4004, ('dbid777','d4')),
  (4005, ('dbid777','d5'));


INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location)
VALUES
  (1001, 1, 4001, '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint),
  (1002, 1, 4002, '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint),
  (1003, 1, 4003, '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint),
  (1004, 1, 4004, '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint),
  (1005, 1488, 4005, '2017-11-19T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint);

INSERT INTO state.sessions
  (point_id, active, start,                     "end",                     bonus_until,               completed, revision, driver_id_id, mode_id, destination_point)
VALUES
  (1001,     True,   '2017-11-19T16:47:54.721', NULL,                      NULL,                      False,     2,        4001,         1,       (1, 2)::db.geopoint),
  (1002,     False,  '2017-11-19T16:47:54.721', NULL,                      NULL,                      False,     3,        4002,         1,       (1, 2)::db.geopoint),
  (1003,     True,   '2017-11-19T16:47:54.721', '2017-11-19T16:27:54.721', NULL,                      True,      4,        4003,         1,       (1, 2)::db.geopoint),
  (1004,     False,  '2017-11-19T16:47:54.721', '2017-11-19T16:47:54.721', NULL,                      False,     5,        4004,         1,       (1, 2)::db.geopoint),
  (1005,     True,   '2017-11-19T16:47:54.721', '2017-11-19T16:57:54.721', '2017-11-19T17:07:54.721', True,      6,        4005,         1488,    (1, 2)::db.geopoint);


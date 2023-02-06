INSERT INTO config.modes
  (mode_id, mode_name,     offer_only, min_allowed_distance, max_allowed_distance, mode_type,                 experimental, tags_prohibited,         work_modes)
VALUES
  (1,       'home',        False,      2000,                 180000,               ('ToPoint')::db.mode_type, False,        NULL,                    ARRAY['orders']),
  (2,       'poi',         False,      2000,                 180000,               ('ToPoint')::db.mode_type, False,        ARRAY['poi_prohibited'], ARRAY['orders']),
  (3,       'my_district', False,      2000,                 180000,               ('InArea')::db.mode_type,  True,         NULL,                    ARRAY['orders']);
;

INSERT INTO config.submodes
  (mode_id, submode_id, submode_name, is_default, "order", is_highlighted)
VALUES
  (3,       1,          '30',         False,      1,       False),
  (3,       2,          '60',         True,       2,       True),
  (3,       3,          '90',         False,      3,       False),
  (2,       4,          'single',     True,       4,       True)
;

INSERT INTO config.usage_rules
  (mode_id, day_usage_limit, week_usage_limit, day_duration_limit_sum, week_duration_limit_sum, change_interval)
VALUES
  (1,       2,               NULL,             NULL,                   NULL,                    '4 days'),
  (2,       1,               7,                NULL,                   NULL,                    NULL),
  (3,       NULL,            NULL,             '120 min',              '360 min',               NULL)
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id,             updated,                   name,          address,          city,   location)
VALUES
  (2001,     1,       IdId('driverSS', '1488'), '2018-11-26T16:47:54.721', 'home_name_1', 'home_address_1', 'city', (1, 2)::db.geopoint)
;

INSERT INTO settings.saved_points
  (saved_point_id, point_id)
VALUES
  (1001,           2001)
 ;

INSERT INTO config.display_rules(
  mode_id,
  image,
  tanker_key,
  tags_permitted,
  tags_prohibited
) VALUES (
  1,
  'follow_track',
  'home.restrictions.track',
  NULL,
  NULL
), (
  1,
  'keep_moving',
  'home.restrictions.move',
  ARRAY['permit_home_move'],
  ARRAY['prohibit_home_move']
), (
  2,
  'follow_track',
  'poi.restrictions.track',
  NULL,
  ARRAY['prohibit_poi_track']
), (
  2,
  'keep_moving',
  'poi.restrictions.move',
  ARRAY['permit_poi_move'],
  NULL
);

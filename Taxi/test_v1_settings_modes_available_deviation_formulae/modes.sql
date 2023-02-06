INSERT INTO config.modes
(
  mode_id,
  mode_name,
  offer_only,
  offer_radius,
  min_allowed_distance,
  max_allowed_distance,
  mode_type
)
VALUES
(
  1, 'home', false, NULL, 2000, 180000, ('ToPoint')::db.mode_type
),
(
  2, 'poi', false, NULL, 2000, 180000, ('ToPoint')::db.mode_type
),
(
  3, 'surge', true, 10000, 2000, 180000, ('ToPoint')::db.mode_type
),
(
  4, 'my_district', false, NULL, 2000, 180000, ('InArea')::db.mode_type
);

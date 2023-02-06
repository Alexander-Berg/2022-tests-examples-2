INSERT INTO config.modes (
  mode_id,
  mode_name,
  offer_only,
  offer_radius,
  min_allowed_distance,
  max_allowed_distance,
  mode_type,
  client_attributes,
  work_modes
) VALUES (
  1,
  'home',
  False,
  NULL,
  2000,
  180000,
  ('ToPoint')::db.mode_type,
  '{"dead10cc": "deadbeef", "navigation": "%DYNAMIC%"}',
  ARRAY['orders']
);

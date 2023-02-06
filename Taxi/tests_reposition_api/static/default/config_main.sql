INSERT INTO config.zones(
  zone_name
) VALUES (
  'moscow'
), (
  'spb'
);

INSERT INTO config.modes(
  mode_id,
  mode_name,
  mode_type,
  offer_only,
  offer_radius,
  min_allowed_distance,
  max_allowed_distance,
  client_attributes,
  work_modes
) VALUES (
  1,
  'home',
  'ToPoint',
  FALSE,
  NULL,
  2000,
  180000,
  '{"dead10cc": "deadbeef"}',
  ARRAY['orders']
), (
  2,
  'poi',
  'ToPoint',
  FALSE,
  NULL,
  2000,
  180000,
  '{"dead10cc": "deadbeef"}',
  ARRAY['orders']
), (
  3,
  'District',
  'InArea',
  FALSE,
  NULL,
  2000,
  180000,
  '{"dead10cc": "deadbeef"}',
  ARRAY['orders']
), (
  4,
  'SuperSurge',
  'ToPoint',
  TRUE,
  300,
  2000,
  180000,
  '{"dead10cc": "deadbeef"}',
  ARRAY['orders']
);

INSERT INTO config.submodes (
  submode_id,
  submode_name,
  mode_id,
  is_default,
  is_highlighted,
  "order"
) VALUES (
  1,
  '30',
  3,
  TRUE,
  TRUE,
  1
), (
  2,
  '60',
  3,
  FALSE,
  FALSE,
  2
), (
  3,
  '90',
  3,
  FALSE,
  FALSE,
  3
);

INSERT INTO settings.driver_ids(
  driver_id_id,
  driver_id
) VALUES (
  1, ('park_id_1', 'profile_id_1')
), (
  2, ('park_id_1', 'profile_id_2')
), (
  3, ('park_id_2', 'profile_id_1')
);

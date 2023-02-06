INSERT INTO config.zones(
  zone_name
) VALUES (
  'moscow'
);

INSERT INTO config.modes(
  mode_name,
  mode_type,
  offer_only
) VALUES (
  'home',
  'ToPoint',
  false
), (
  'District',
  'InArea',
  false
);

INSERT INTO config.submodes(
  submode_name,
  mode_id,
  is_default
) VALUES (
  'fast',
  1,
  true
), (
  'slow',
  1,
  false
), (
  '30',
  2,
  false
), (
  '90',
  2,
  false
);

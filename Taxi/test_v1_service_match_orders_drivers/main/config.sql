INSERT INTO config.zones(
  zone_name
) VALUES (
  'moscow'
), (
  'spb'
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
  'poi',
  'ToPoint',
  false
), (
  'District',
  'InArea',
  false
), (
  'surge',
  'ToPoint',
  true
);

INSERT INTO config.submodes(
  submode_name,
  mode_id,
  is_default
) VALUES (
  'fast',
  2,
  true
), (
  'slow',
  2,
  false
), (
  '30',
  3,
  false
), (
  '90',
  3,
  false
);

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
  'surge',
  'ToPoint',
  true
), (
  'District',
  'InArea',
  false
);

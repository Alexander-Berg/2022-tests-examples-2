INSERT INTO config.zones
(
  zone_id,
  parent_zone,
  zone_name
)
VALUES
(
  nextval('config.zones_zone_id_seq'::regclass),
  NULL,
  '__default__'
);

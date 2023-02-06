INSERT INTO config.zones
  (zone_id, parent_zone, zone_name)
VALUES
  (2, NULL, 'svo')
;

INSERT INTO config.forbidden_zones
  (mode_id, zone_id, alert)
VALUES
  (2, 2, '!!!')
;

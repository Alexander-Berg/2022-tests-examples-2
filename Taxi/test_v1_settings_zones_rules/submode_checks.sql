INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id, arrival_id, immobility_id, submode_id, surge_arrival_id, out_of_area_id, route_id, transporting_arrival_id, antisurge_arrival_id)
VALUES
  (3, 1, 2, 2, 2, NULL, 2, 1, 1, 1, 1),
  (3, 1, 1, 1, 1, 3,    1, 2, 2, 2, 2);

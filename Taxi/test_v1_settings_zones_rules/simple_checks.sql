INSERT INTO config.check_rules
  (zone_id, mode_id, submode_id, duration_id, arrival_id, immobility_id, surge_arrival_id, out_of_area_id, route_id, surge_arrival_local_id, transporting_arrival_id, antisurge_arrival_id)
VALUES
  (1,       1,       NULL,       1,           1,          1,             1,                1,              1,        1,                      1,                       1),
  (1,       1,       1,          1,           2,          1,             NULL,             NULL,           NULL,     1,                      1,                       NULL),
  (1,       1,       2,          2,           2,          2,             2,                2,              2,        1,                      2,                       2);

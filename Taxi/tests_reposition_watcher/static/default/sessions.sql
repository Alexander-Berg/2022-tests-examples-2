INSERT INTO state.sessions
    (session_id, dbid_uuid, start, reposition_source_point, reposition_dest_point,
      reposition_dest_radius, mode_id,
     duration_id, arrival_id, immobility_id, surge_arrival_id, out_of_area_id, route_id,
     tariff_class)
  VALUES
    (1, ('dbid777','888'), '2010-04-04 06:00:00', '(1,2)', '(3,4)', 12, 'home', 2, NULL, NULL, NULL, NULL, NULL, 'econom'),
    (22, ('1488', 'driverSS'), '2010-04-04 06:00:00', '(1,2)', '(3,4)', 12, 'poi', 1, NULL, 1, NULL, 2, NULL, 'econom'),
    (32, ('1488','driverSS2'), '2010-04-04 06:00:00', '(1,2)', '(3,4)', 12, 'surge', 3, 1, 2, 1, 1, 2, 'econom')
;

INSERT INTO state.sessions_to_reposition_watcher
  (session_id, is_stop_action, duration_id, arrival_id, immobility_id, surge_arrival_id, out_of_area_id, route_id, created_at)
VALUES
  (2005,       FALSE,          12,          21,         31,            41,               NULL,           NULL,     '2018-10-12T16:01:11.540859'),
  (2006,       FALSE,          13,          21,         31,            NULL,             NULL,           NULL,     '2018-10-14T06:01:11.540859'),
  (2007,       TRUE,           12,          21,         31,            NULL,             NULL,           NULL,     '2018-10-13T12:01:12.540859'),
  (2009,       FALSE,          12,          21,         31,            NULL,             NULL,           NULL,     '2018-10-13T12:01:11.540859');

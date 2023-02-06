INSERT INTO state.sessions_to_reposition_watcher
  (session_id, is_stop_action, duration_id, arrival_id, immobility_id, surge_arrival_id, out_of_area_id, route_id, created_at)
VALUES
  (2009,       TRUE,           11,          21,         31,            41,               NULL,           61,       '2018-10-11T16:02:11.540859'),
  (2003,       FALSE,          11,          21,         31,            41,               51,             61,       '2018-10-11T16:01:11.540859'),
  (2004,       FALSE,          12,          21,         31,            41,               51,             NULL,     '2018-10-12T16:01:11.540859'),
  (2005,       FALSE,          12,          21,         31,            41,               NULL,           NULL,     '2018-10-13T16:01:11.540859'),
  (2006,       FALSE,          13,          21,         31,            NULL,             NULL,           NULL,     '2018-10-13T06:01:11.540859'),
  (2007,       TRUE,           12,          21,         31,            NULL,             NULL,           NULL,     '2018-10-13T12:01:11.540859'),
  (2007,       FALSE,          12,          21,         31,            NULL,             NULL,           NULL,     '2018-10-13T12:01:11.540859'),
  (2002,       FALSE,          12,          21,         31,            NULL,             NULL,           NULL,     '2018-10-13T12:01:11.540859'),
  (2008,       TRUE,           12,          21,         31,            NULL,             NULL,           NULL,     '2018-10-13T12:01:11.540859');

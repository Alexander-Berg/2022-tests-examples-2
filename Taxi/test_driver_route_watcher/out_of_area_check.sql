INSERT INTO checks.out_of_area
  (out_of_area_id, first_warnings, last_warnings, min_distance_from_border, time_out_of_area)
VALUES
  (101,            3,              2,             10,                       interval '10 seconds')
;


INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (1401, 1, IdId('888', 'dbid777'), '09-01-2018', 'dbid777_888_home', 'some home address', 'Postgresql', (3, 4), NULL);

INSERT INTO state.sessions
  (session_id, driver_id_id, active, point_id, start, "end", mode_id, destination_point, destination_radius)
VALUES
  (1501, IdId('888', 'dbid777'), TRUE, 1401, '2017-10-18T07:30:00+0000', NULL, 1, (3, 4), 12)
;


INSERT INTO state.checks
  (session_id, out_of_area_id, checking, last_check,                 out_of_area_check_data)
VALUES
  (1501,       101,            NULL,     '2017-10-18T07:33:00+0000', ('2017-10-18T07:33:59+0000',0))
;


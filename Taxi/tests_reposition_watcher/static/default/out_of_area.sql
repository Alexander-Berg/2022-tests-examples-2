INSERT INTO checks.conditions(
    condition_id,
    is_allowed_on_order) VALUES
    (201, true);


INSERT INTO checks.config(
    config_id,
    dry_run,
    info_push_count,
    warn_push_count,
    send_push) VALUES
    (201, false, 0, 0, true);

INSERT INTO checks.out_of_area (
  check_id,
  condition_id,
  config_id,
  min_distance_from_border,
  time_out_of_area) VALUES
  (101, 201, 201, 10, make_interval(mins => 15));

INSERT INTO state.out_of_area(
    state_id,
    last_check,
    violations) VALUES
    (101, '2017-10-18T07:33:00+0000', 0);

INSERT INTO state.sessions(session_id, out_of_area_id,dbid_uuid, start,
    reposition_source_point, reposition_dest_point, reposition_dest_radius, mode_id, tariff_class) VALUES
(1511, 101, ('dbid777','999'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'home', 'econom');


INSERT INTO state.immobility(immobility_violations)  SELECT(0) FROM generate_series(11,11);
INSERT INTO state.out_of_area (violations) SELECT(0) FROM generate_series(11,11);
INSERT INTO state.route(last_checks_count) SELECT(0) FROM generate_series(11,11);
INSERT INTO state.checks(session_id, immobility_state_id, route_state_id, out_of_area_state_id) SELECT i+1500, i, i, i FROM generate_series(11, 11) i;

update state.checks SET  out_of_area_state_id = 101 where session_id = 1511;


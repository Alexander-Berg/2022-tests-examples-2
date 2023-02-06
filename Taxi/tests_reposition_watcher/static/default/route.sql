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
    (201, false, 1, 1, true);

INSERT INTO checks.route (
        check_id,
        condition_id,
        config_id,
        check_interval,
        max_last_checks_count,
        max_violations_count,
        speed_dist_range,
        speed_dist_abs_range,
        speed_eta_range,
        speed_eta_abs_range,
        range_checks_compose_operator,
        speed_checks_compose_operator ) VALUES
  (101, 201, 201, '60 secs', 4, 3, ('-Infinity', 20)::checks.double_range, (1, 20)::checks.double_range, (-2, 5)::checks.double_range, (1, 5)::checks.double_range, 'AND', 'OR');

INSERT INTO state.route(
    state_id,
    last_check,
    start_time,
    violations_count) VALUES
    (101, '2018-11-26T07:59:00+0000', '2018-11-26T07:59:00+0000', 0);

INSERT INTO state.sessions(session_id, route_id,dbid_uuid, start,
    reposition_source_point, reposition_dest_point, reposition_dest_radius, mode_id, tariff_class, drw_state) VALUES
(1511, 101, ('dbid777','999'), '2018-11-26T07:59:00+0000', point(30,60), point(30,60), 12, 'home', 'econom', 'Disabled');


INSERT INTO state.immobility(immobility_violations)  SELECT(0) FROM generate_series(11,11);
INSERT INTO state.out_of_area(violations) SELECT(0) FROM generate_series(11,11);
INSERT INTO state.route(last_checks_count) SELECT(0) FROM generate_series(11,11);
INSERT INTO state.checks(session_id, immobility_state_id, out_of_area_state_id, route_state_id) SELECT i+1500, i, i, i FROM generate_series(11, 11) i;

update state.checks SET  route_state_id = 101 where session_id = 1511;


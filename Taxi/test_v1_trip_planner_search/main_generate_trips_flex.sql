INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.653044, 55.742924)),
    (2, point(37.650962, 55.743710)),
    (3, point(37.648669, 55.745202)),
    (4, point(37.647022, 55.747177)),
    (5, point(37.643891, 55.749957)),
    (6, point(37.641166, 55.751533)),
    (7, point(37.639805, 55.752609)),
    (8, point(37.637255, 55.753961));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id, is_terminal
)
VALUES
    (1, 1, 'stop1', NULL, FALSE),
    (2, 2, 'stop2', NULL, FALSE),
    (3, 3, 'stop3', NULL, TRUE),
    (4, 4, 'stop4', NULL, FALSE),
    (5, 5, 'stop5', NULL, FALSE),
    (6, 6, 'stop6', NULL, FALSE),
    (7, 7, 'stop7', NULL, FALSE),
    (8, 8, 'stop8', NULL, FALSE);

INSERT INTO config.routes (
    route_id, name, is_dynamic
)
VALUES
    (1, 'route1', True)
;

INSERT INTO config.route_points (
  route_id, point_id, point_order
)
VALUES
  (1, 1, NULL),
  (1, 2, NULL),
  (1, 3, NULL),
  (1, 4, NULL),
  (1, 5, NULL),
  (1, 6, NULL),
  (1, 7, NULL),
  (1, 8, NULL)
;

INSERT INTO state.route_views (
    route_id, current_view, traversal_plan
)
VALUES
    (1, ARRAY[3], ROW(ARRAY[
        (3, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan)
;

INSERT INTO state.shuttles (
    driver_id, route_id, is_fake, capacity, ticket_length, view_id
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, FALSE, 5, 3, 1);

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 0, 3, 3, NOW(), NOW());

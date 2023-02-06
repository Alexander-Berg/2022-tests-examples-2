INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643037,55.734242)),
    (5, point(37.642790,55.734062)),
    (6, point(37.642023,55.734035)),
    (7, point(37.639896,55.737345)),
    (8, point(37.641867,55.737651));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', NULL),
    (5, 7, 'stop5', NULL),
    (6, 8, 'stop6', NULL);

INSERT INTO config.routes (
    route_id, name, is_cyclic
)
VALUES
    (1, 'route1', TRUE);

INSERT INTO config.route_points (
    route_id, point_id, point_order
)
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4),
    (1, 5, 5),
    (1, 6, 6),
    (1, 7, 7),
    (1, 8, 8);

INSERT INTO state.shuttles (
    shuttle_id, driver_id, route_id, capacity, ticket_length, work_mode, subscription_id
)
VALUES
    (1, ('dbid_0', 'uuid_1')::db.driver_id, 1, 16, 3, 'shuttle_fix', 1);

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 1, 1, 3, NOW(), NOW())
;

INSERT INTO state.pauses (
    pause_id,
    shuttle_id,
    pause_requested,
    expected_pause_start,
    pause_started,
    expected_pause_finish,
    pause_finished
) VALUES (
    1,
    1,
    '2020-06-04T11:30:55+0000',
    '2020-06-04T11:50:55+0000',
    '2020-06-04T11:50:55+0000',
    '2020-06-04T12:20:55+0000',
    NULL
);

UPDATE state.shuttles
SET pause_state = 'in_work',
    pause_id = 1
WHERE shuttle_id = 1;

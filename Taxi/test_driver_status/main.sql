INSERT INTO config.points (
    point_id,
    position
)
VALUES (
    1,
    point(30, 60)
);

INSERT INTO config.stops (
    stop_id,
    point_id,
    name
)
VALUES (
    1,
    1,
    'main_stop'
);

INSERT INTO config.routes (
    route_id,
    name
)
VALUES (
    1,
    'main_route'
);

INSERT INTO config.route_points (
  route_id,
  point_id,
  point_order
)
VALUES (
  1,
  1,
  1
);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length
)
VALUES (
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    16,
    3
);

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 0, 1, 1, NOW(), NOW())
;

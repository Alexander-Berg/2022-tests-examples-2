INSERT INTO config.points (
    point_id,
    position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643148,55.734349));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name
)
VALUES
    (1, 1, 'main_stop'),
    (2, 2, 'stop2'),
    (3, 3, 'stop3'),
    (4, 4, 'stop4');

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
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4);

WITH shuttle_ins AS (
  INSERT INTO state.shuttles (
    driver_id,
    route_id,
    capacity,
    ticket_length,
    work_mode
  )
  VALUES (
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    16,
    3,
    'shuttle_fix'
  )
  RETURNING
    shuttle_id
)
INSERT INTO state.shuttle_trip_progress (
  shuttle_id,
  begin_stop_id,
  lap,
  next_stop_id,
  updated_at,
  advanced_at
)
SELECT
  shuttle_ins.shuttle_id,
  1,
  1,
  2,
  NOW(),
  NOW()
FROM
  shuttle_ins
;

INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(30.00, 60.00)),
    (2, point(30.01, 60.01)),
    (3, point(30.02, 60.02)),
    (4, point(30.03, 60.03)),
    (5, point(30.04, 60.04)),
    (6, point(30.05, 60.05)),
    (7, point(30.06, 60.06)),
    (8, point(30.07, 60.07)),
    (9, point(30.08, 60.08));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', 'stop__1'),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', 'stop__4'),
    (5, 8, 'stop5', 'stop__5'),
    (6, 9, 'stop6', 'stop__6');

INSERT INTO config.schedules (schedule)
VALUES ('{
  "timezone":"UTC",
  "intervals": [{
    "exclude": false,
    "day": [4]
  }, {
    "exclude": false,
    "daytime": [{
      "from": "11:30:00",
      "to": "11:30:00"
    }, {
      "from": "12:00:00",
      "to": "12:00:00"
    }, {
      "from": "12:30:00",
      "to": "12:30:00"
    }
    ]
  }]}'::jsonb), ('{
  "timezone":"UTC",
  "intervals": [{
    "exclude": false,
    "day": [4]
  }, {
    "exclude": false,
    "daytime": [{
      "from": "12:01:00",
      "to": "12:01:00"
    }, {
      "from": "12:15:00",
      "to": "12:15:00"
    }, {
      "from": "12:45:00",
      "to": "12:45:00"
    }
    ]
  }]}'::jsonb), ('{
  "timezone":"UTC",
  "intervals": [{
    "exclude": false,
    "day": [4]
  }, {
    "exclude": false,
    "daytime": [{
      "from": "11:50:00",
      "to": "11:50:00"
    }, {
      "from": "12:20:00",
      "to": "12:20:00"
    }, {
      "from": "12:50:00",
      "to": "12:50:00"
    }, {
      "from": "13:20:00",
      "to": "13:20:00"
    }
    ]
  }]}'::jsonb), ('{
  "timezone":"UTC",
  "intervals": [{
    "exclude": false,
    "day": [4]
  }, {
    "exclude": false,
    "daytime": [{
      "from": "11:29:59",
      "to": "11:29:59"
    }, {
      "from": "11:59:59",
      "to": "11:59:59"
    }, {
      "from": "12:29:99",
      "to": "12:29:99"
    }
    ]
  }]}'::jsonb);

INSERT INTO config.routes (
    route_id, name, is_cyclic
)
VALUES
    (1, 'route1', True);

INSERT INTO config.route_stops_schedules (
    route_id, stop_id, schedule_id
)
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 5, 3);

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
  (1, 8, 8),
  (1, 9, 9);

INSERT INTO state.shuttles (
    driver_id, route_id, is_fake, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, False, 16, 3);
-- TODO(dvinokurov): adapt the test for the drivers below
--     (('dbid1', 'uuid1')::db.driver_id, 1, False, 16, 3),
--     (('dbid2', 'uuid2')::db.driver_id, 1, False, 16, 3);

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 0, 1, 1, NOW(), NOW());

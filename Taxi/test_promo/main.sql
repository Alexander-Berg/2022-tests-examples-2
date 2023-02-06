INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(30.00, 60.00)),
    (2, point(30.01, 60.01)),
    (3, point(30.02, 60.02));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 2, 'stop2', 'stop__2'),
    (3, 3, 'stop3', 'stop__3');

INSERT INTO config.schedules (schedule)
VALUES ('{
  "timezone":"UTC",
  "intervals": [{
    "exclude": false,
    "day": [4]
  }, {
    "exclude": false,
    "daytime": [{
        "from": "11:00:00",
        "to": "18:00:00"
      }
    ]
  }],
  "repeat":{
    "interval": 1800,
    "origin": "start"
  }}'::jsonb);

INSERT INTO config.routes (
    route_id, name
)
VALUES
    (1, 'route1');

INSERT INTO config.route_points (
  route_id, point_id, point_order
)
VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 3);

INSERT INTO state.shuttles (
	driver_id, route_id, capacity, ticket_length
)
VALUES
	(('dbid1', 'uuid1'), 1, 16, 4);

INSERT INTO state.matching_offers (
    offer_id,
    yandex_uid,
    shuttle_id,
    route_id,
    order_point_a,
    order_point_b,
    pickup_stop_id,
    pickup_lap,
    dropoff_stop_id,
    dropoff_lap,
    price,
    created_at,
    expires_at
)
VALUES
	(
		'7c76c53b-98bb-481c-ac21-0555c5e51d10',
	    '1234567',
		1,
	    1,
		point(30.01, 50.01),
		point(35.0, 65.0),
		1,
		1,
		3,
		1,
		(20.0, 'RUB')::db.trip_price,
		'2020-05-28T10:40:55',
		'2020-05-28T10:55:55'
	);

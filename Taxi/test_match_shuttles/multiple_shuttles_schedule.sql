INSERT INTO config.schedules (schedule)
VALUES ('{
  "timezone":"UTC",
  "intervals": [{
    "exclude": false,
    "day": [4]
  }, {
    "exclude": false,
    "daytime": [{
      "from": "10:30:00",
      "to": "10:30:00"
    }, {
      "from": "10:50:00",
      "to": "10:50:00"
    }, {
      "from": "11:10:00",
      "to": "11:10:00"
    }
    ]
  }]}'::jsonb);

INSERT INTO config.route_stops_schedules (
    route_id, stop_id, schedule_id
)
VALUES
(1, 3, 1);

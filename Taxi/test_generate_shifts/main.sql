INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since,
    deprecated_since,
    personal_goal,
    generated_up_to,
    max_pauses_allowed,
    pause_duration,
    simultaneous_pauses_per_shift
) VALUES ( -- 1
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'route1',
    '{
      "timezone":"UTC",
      "intervals": [{
        "exclude": false,
        "day": [4]
      }, {
        "exclude": false,
        "daytime": [{
          "from": "10:30:00",
          "to": "14:00:00"
        }
        ]
      }]}'::JSONB,
    10,
    '2020-05-28T10:40:55+0000',
    NULL,
    NULL,
    NULL,
    1,
    '15 minutes'::interval,
    1
), ( -- 1
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    'route2',
    '{
      "timezone":"UTC",
      "intervals": [{
        "exclude": false,
        "day": [2]
      }, {
        "exclude": false,
        "daytime": [{
          "from": "11:30:00",
          "to": "12:00:00"
        }
        ]
      }]}'::JSONB,
    11,
    '2020-05-28T10:40:55+0000',
    '2020-06-10T10:40:55+0000',
    '(30,50)'::db.driver_personal_goal,
    NULL,
    10,
    '15 minutes'::interval,
    5
), ( -- 1
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    'route3',
    '{
      "timezone":"UTC",
      "intervals": [{
        "exclude": false,
        "day": [6]
      }, {
        "exclude": false,
        "daytime": [{
          "from": "12:30:00",
          "to": "13:00:00"
        }
        ]
      }]}'::JSONB,
    12,
    '2020-05-28T10:40:55+0000',
    NULL,
    NULL,
    '2020-06-03T10:40:55+0000',
    1,
    '30 minutes'::interval,
    2
), ( -- 0
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    'route4',
    '{
      "timezone":"UTC",
      "intervals": [{
        "exclude": false,
        "day": [5]
      }, {
        "exclude": false,
        "daytime": [{
          "from": "10:30:00",
          "to": "14:00:00"
        }
        ]
      }]}'::JSONB,
    10,
    '2020-06-10T10:40:55+0000',
    NULL,
    NULL,
    NULL,
    3,
    '11 minutes'::interval,
    3
), ( -- 0
    '2fef68c9-25d0-4174-9dd0-bdd1b3730770',
    'route5',
    '{
      "timezone":"UTC",
      "intervals": [{
        "exclude": false,
        "day": [5]
      }, {
        "exclude": false,
        "daytime": [{
          "from": "10:30:00",
          "to": "14:00:00"
        }
        ]
      }]}'::JSONB,
    10,
    '2020-06-02T10:40:55+0000',
    NULL,
    NULL,
    '2020-06-10T10:40:55+0000',
    33,
    '33 minutes'::interval,
    33
), ( -- 0
    '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
    'route6',
    '{
      "timezone":"UTC",
      "intervals": [{
        "exclude": false,
        "day": [2]
      }, {
        "exclude": false,
        "daytime": [{
          "from": "11:30:00",
          "to": "12:00:00"
        }
        ]
      }]}'::JSONB,
    11,
    '2020-05-28T10:40:55+0000',
    '2020-05-29T10:40:55+0000',
    NULL,
    NULL,
    0,
    '0 seconds'::interval,
    0
);

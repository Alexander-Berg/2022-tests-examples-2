INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since,
    deprecated_since,
    personal_goal,
    max_pauses_allowed,
    pause_duration,
    simultaneous_pauses_per_shift
) VALUES (
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
     '2021-05-28T10:40:55+0000',
     NULL,
     1,
     '15 minutes'::interval,
     1
 ),
 (
     '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
     'route1',
     '{
       "timezone":"UTC",
       "intervals": [{
         "exclude": false,
         "day": [5, 6, 7]
       }, {
         "exclude": false,
         "daytime": [{
           "from": "10:30:00",
           "to": "14:00:00"
         }
         ]
       }]}'::JSONB,
     11,
     '2020-05-28T10:40:55+0000',
     NULL,
     '(30,50)'::db.driver_personal_goal,
     2,
     '30 minutes'::interval,
     2
);

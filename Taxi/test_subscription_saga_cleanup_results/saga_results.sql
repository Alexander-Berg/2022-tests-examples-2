INSERT INTO state.saga_results(saga_id, status, park_id, driver_id,
                               mode_change_token, created_at)
VALUES ('1', 'executed', 'dbid', 'uuid', '1', '2020-04-04 01:00:00+03'),
       ('2', 'compensated', 'dbid', 'uuid', '2', '2020-04-04 02:00:00+03'),
       ('3', 'executed', 'dbid', 'uuid', '3', '2020-04-04 03:00:00+03'),
       ('4', 'executed', 'dbid', 'uuid', '4', '2020-04-04 04:00:00+03'),
       ('5', 'compensated', 'dbid1', 'uuid', '5', '2020-04-04 05:00:00+03'),
       ('6', 'executed', 'dbid', 'uuid1', '6', '2020-04-04 06:00:00+03'),
       ('7', 'executed', 'dbid', 'uuid', '7', '2020-04-04 07:00:00+03');

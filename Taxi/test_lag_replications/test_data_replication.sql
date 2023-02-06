INSERT INTO courier_groups
(id, name)
VALUES (1, 'courier_group');

INSERT INTO couriers
(id, group_id, region_id, courier_type, name, work_status, created_at, updated_at, service, external_id, pool_name)
VALUES
       (1, 1, 1, 'pedestrian', 'Vasya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID', 'POOL_NAME'),
       (2, 1, 1, 'pedestrian', 'Petya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_2', 'POOL_NAME'),
       (3, 1, 1, 'bicycle', 'Ivan', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_3', 'POOL_NAME');

INSERT INTO courier_active_shifts
(id, courier_id, shift_id, state, high_priority,
 zone_id, metagroup_id, zone_group_id, unpauses_at, closes_at, started_at,
 created_at, updated_at)
VALUES (1, 1, 1, 'closed', true, 1, '1', 1, null, '2020-11-27T18:41:25+03:00',
        '2020-11-27T06:40:50+03:00',
        '2020-11-27T06:40:50+03:00',
        '2020-11-27T19:40:50+03:00'),
       (2, 2, 2, 'in_progress', false, 1, '1', 1, null, '2020-11-30T18:41:25+03:00',
        '2020-11-30T06:40:50+03:00',
        '2020-11-30T06:40:50+03:00',
        '2020-11-30T19:40:50+03:00'),
       (3, 3, 3, 'in_progress', false, 1, '1', 1, null, '2020-12-01T18:41:25+03:00',
        '2020-12-01T06:40:50+03:00',
        '2020-12-01T06:40:50+03:00',
        '2020-12-01T19:40:50+03:00');

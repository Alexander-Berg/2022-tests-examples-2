INSERT INTO courier_groups
(id, name)
VALUES (1, 'courier_group');

INSERT INTO couriers
(id, group_id, region_id, courier_type, name, work_status, created_at, updated_at, service, external_id, pool_name)
VALUES
    (1, 1, 1, 'pedestrian', 'Vasya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID', 'POOL_NAME'),
    (2, 1, 1, 'pedestrian', 'Petya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_2', 'POOL_NAME'),
    (3, 1, 1, 'bicycle', 'Ivan', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_3', 'POOL_NAME'),
    (4, 1, 1, 'pedestrian', 'Artem', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_4', 'POOL_NAME'),
    (5, 1, 1, 'bicycle', 'Vadim', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_5', 'POOL_NAME');

INSERT INTO courier_active_shifts
(id, courier_id, shift_id, state, high_priority,
 zone_id, metagroup_id, zone_group_id, unpauses_at, closes_at, started_at,
 created_at, updated_at)
VALUES (1, 1, 1, 'closed', true, 1, '1', 1, null, '2021-08-11T13:40:50Z',
        '2020-11-27T06:40:50Z',
        '2020-11-27T06:40:50Z',
        '2020-11-27T19:40:50Z'),
       (2, 2, 2, 'in_progress', false, 1, '1', 1, null, '2021-08-11T13:40:50Z',
        '2020-11-30T06:40:50Z',
        '2020-11-30T06:40:50Z',
        '2020-11-30T19:40:50Z'),
       (3, 3, 3, 'paused', false, 1, '1', 1, null, '2021-08-11T13:40:50Z',
        '2020-12-01T06:40:50Z',
        '2020-12-01T06:40:50Z',
        '2020-12-01T19:40:50Z'),
       (4, 4, 4, 'in_progress', false, 1, '1', 1, null, '2021-08-11T14:40:00+03:00',
        '2020-12-01T06:40:50Z',
        '2020-12-01T06:40:50Z',
        '2020-12-01T19:40:50Z'),
       (5, 5, 5, 'in_progress', false, 1, '1', 1, null, '2021-08-11T11:40:00Z',
        '2020-12-01T06:40:50Z',
        '2020-12-01T06:40:50Z',
        '2020-12-01T19:40:50Z');

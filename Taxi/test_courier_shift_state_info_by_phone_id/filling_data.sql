SET TIME ZONE 'Europe/Moscow';

INSERT INTO courier_groups
(id, name)
VALUES (1, 'courier_group');

INSERT INTO couriers
(id, group_id, region_id, courier_type, name, work_status, created_at, updated_at, service, external_id, pool_name)
VALUES
    (1, 1, 1, 'pedestrian', 'Vasya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_1', 'eda'),
    (2, 1, 1, 'pedestrian', 'Petya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_2', 'eda'),
    (3, 1, 1, 'bicycle', 'Ivan', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_3', 'eda'),
    (4, 1, 1, 'pedestrian', 'Artem', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_4', 'eda'),
    (5, 1, 1, 'bicycle', 'Vadim', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_5', 'eda'),
    (6, 1, 1, 'bicycle', 'Vadim', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_6', 'eda');

INSERT INTO courier_shifts
(id, courier_offline_time, courier_id, region_id, zone_id, status, start_location_id, service, start_time, end_time, date)
VALUES
    (1, 1, 1, 1, 1, 'in_progress', 1, 'eda', '2021-08-06T10:20:00Z', '2021-08-06T20:40:00Z', '2021-08-06'),
    (2, 1, 2, 2, 2, 'on_pause', 1, 'eda', '2021-08-06T10:20:00Z', '2021-08-06T23:40:00Z', '2021-08-06'),
    (3, 1, 3, 3, 3, 'planned', 1, 'eda', '2021-08-06T10:20:00Z', '2021-08-06T08:40:00Z', '2021-08-06'),
    (4, 1, 4, 1, 1, 'planned', 1, 'eda', '2021-08-06T10:20:00Z', '2021-08-06T20:40:00Z', '2021-08-06'),
    (5, 1, 5, 2, 2, 'planned', 1, 'eda', '2021-08-06T10:20:00Z', '2021-08-06T23:40:00Z', '2021-08-06'),
    (6, 1, 6, 3, 3, 'in_progress', 1, 'eda', '2021-08-06T10:20:00Z', '2021-08-06T08:40:00Z', '2021-08-06'),
    (7, 1, 6, 3, 3, 'planned', 1, 'eda', '2021-08-06T10:20:00Z', '2021-08-06T08:40:00Z', '2021-08-06');

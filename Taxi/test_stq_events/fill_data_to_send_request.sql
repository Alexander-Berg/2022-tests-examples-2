INSERT INTO performer_quality_controls
(performer_id,
 control_type,
 next_control_at)
VALUES ('1', 'some_other_control', '2021-09-10T13:00:00-07:00');

-- '2021-09-10T12:00:00+03:00' - now

INSERT INTO courier_groups
(id, name)
VALUES (1, 'courier_group');

INSERT INTO couriers
(id, group_id, region_id, courier_type, name, work_status, created_at, updated_at, service, external_id, pool_name)
VALUES (1, 1, 1, 'pedestrian', 'Vasya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats',
        'EXTERNAL_ID', 'POOL_NAME'),
       (2, 1, 1, 'pedestrian', 'Petya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats',
        'EXTERNAL_ID_2', 'POOL_NAME'),
       (3, 1, 1, 'bicycle', 'Ivan', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats',
        'EXTERNAL_ID_3', 'POOL_NAME');


INSERT INTO courier_shifts
(id,
 courier_offline_time,
 courier_id,
 status,
 region_id,
 zone_id,
 date,
 courier_type,
 parent_id,
 mass_upload_id,
 type,
 pool,
 logistics_group_id,
 effective_logistics_group_id,
 start_location_id,
 service
)
VALUES (1, 1, 1, 'in_progress', 1, 1, '2020-11-27T00:00:00+00:00',
        1, 1, 1, 'planned', 'courier', 1, 1, 1, 'eda');

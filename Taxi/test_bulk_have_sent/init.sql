-- First group --
drop table if exists crm_hub.batch_101_102_global_control_103;
create table crm_hub.batch_101_102_global_control_103(
    id integer,
    status text
);
insert into crm_hub.batch_101_102_global_control_103 (id, status) values
(1, 'FAIL'),
(2, 'FAIL');
-----------------------------------------------------
drop table if exists crm_hub.batch_101_102_local_control_103;
create table crm_hub.batch_101_102_local_control_103(
    id integer,
    status text
);
insert into crm_hub.batch_101_102_local_control_103 (id, status) values
(1, 'FAIL'),
(2, 'SKIPPED');
-----------------------------------------------------
drop table if exists crm_hub.batch_101_102_local_testing_103;
create table crm_hub.batch_101_102_local_testing_103(
    id integer,
    status text
);
insert into crm_hub.batch_101_102_local_testing_103 (id, status) values
(1, 'SKIPPED'),
(2, 'SKIPPED');

-- Second group --
drop table if exists crm_hub.batch_101_103_global_control_104;
create table crm_hub.batch_101_103_global_control_104(
    id integer,
    status text
);
insert into crm_hub.batch_101_103_global_control_104 (id, status) values
(1, 'FAIL'),
(2, 'FAIL');
-----------------------------------------------------
drop table if exists crm_hub.batch_101_103_local_control_104;
create table crm_hub.batch_101_103_local_control_104(
    id integer,
    status text
);
insert into crm_hub.batch_101_103_local_control_104 (id, status) values
(1, 'FAIL'),
(2, 'SUCCESS');
-----------------------------------------------------
drop table if exists crm_hub.batch_101_103_local_testing_104;
create table crm_hub.batch_101_103_local_testing_104(
    id integer,
    status text
);
insert into crm_hub.batch_101_103_local_testing_104 (id, status) values
(1, 'SKIPPED'),
(2, 'SKIPPED');

-----------------------------------------------------
INSERT INTO crm_hub.batch_sending (
    id,
    campaign_id,
    group_id,
    start_id,
    pg_table,

    filter,
    yt_table,
    yt_test_table,
    state,
    entity_type,
    channel,
    channel_info,
    group_type,
    processing_chunk_size,
    use_policy,
    created_at,
    updated_at
)
VALUES
(
    '00000000000000000000000000000001',
    101,
    102,
    103,
    'batch_101_102_global_control_103',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000002',
    101,
    102,
    103,
    'batch_101_102_local_control_103',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000003',
    101,
    102,
    103,
    'batch_101_102_local_testing_103',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
-- duplicate sending --
(
    '00000000000000000000000000000004',
    101,
    102,
    103,
    'batch_101_102_local_testing_103',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
-- without result table --
(
    '00000000000000000000000000000005',
    101,
    102,
    103,
    'batch_101_102_no_result_103',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),


-----------------------------------------------------


(
    '00000000000000000000000000000006',
    101,
    103,
    104,
    'batch_101_103_global_control_104',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    False,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000007',
    101,
    103,
    104,
    'batch_101_103_local_control_104',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    False,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000008',
    101,
    103,
    104,
    'batch_101_103_local_testing_104',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    False,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000009',
    101,
    103,
    104,
    'batch_101_103_local_testing_104',

    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    False,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
);

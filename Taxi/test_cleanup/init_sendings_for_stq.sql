INSERT INTO crm_hub.batch_sending (
    id,
    campaign_id,
    group_id,
    filter,
    yt_table,
    yt_test_table,
    pg_table,
    state,
    use_policy,
    entity_type,
    group_type,
    channel,
    processing_chunk_size,
    channel_info,
    report_extra,
    created_at,
    updated_at,
    replication_state,
    cleanup_state,
    logic_version
)
VALUES
(
    '00000000000000000000000000000001', -- no tables for this sending
    '00',
    '00',
    'group0',
    '//cmp_0_seg',
    '//cmp_0_seg_verification',
    'batch_00_00',
    'FINISHED',
    false,
    'driver',
    'testing',
    'push',
    0,
    '{"channel_name": "driver_push"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00',
    'NEW',
    'PROCESSING',
    null
),
(
    '00000000000000000000000000000002',
    '11',
    '22',
    'group1',
    '//cmp_1_seg',
    '//cmp_1_seg_verification',
    'batch_11_22',
    'FINISHED',
    false,
    'driver',
    'testing',
    'push',
    0,
    '{"channel_name": "driver_push"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00',
    'NEW',
    'PROCESSING',
    null
),
(   -- sending cleanup should be skipped due to ERROR cleanup state
    '00000000000000000000000000000003',
    '33',
    '44',
    'group2',
    '//cmp_3_seg',
    '//cmp_3_seg_verification',
    'batch_33_44',
    'FINISHED',
    false,
    'driver',
    'testing',
    'sms',
    0,
    '{"channel_name": "driver_sms"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00',
    'NEW',
    'ERROR',
    null
),
(   -- sending replication should be skipped due to DONE replication state
    '00000000000000000000000000000004',
    '55',
    '66',
    'group2',
    '//cmp_4_seg',
    '//cmp_4_seg_verification',
    'batch_55_66',
    'FINISHED',
    false,
    'driver',
    'testing',
    'sms',
    0,
    '{"channel_name": "driver_sms"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00',
    'DONE',
    'PROCESSING',
    null
),
(   -- sending replication should be skipped due to no path config for specified entity type
    '00000000000000000000000000000005',
    '77',
    '88',
    'group2',
    '//cmp_4_seg',
    '//cmp_4_seg_verification',
    'batch_77_88',
    'FINISHED',
    false,
    'eatsuser',
    'testing',
    'sms',
    0,
    '{"channel_name": "driver_sms"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00',
    'NEW',
    'PROCESSING',
    null
),
(   -- sending replication should be skipped due to it being verify sending
    '00000000000000000000000000000006',
    '123',
    '234',
    'group2',
    '//cmp_4_seg',
    '//cmp_4_seg_verification',
    'batch_verify_1',
    'FINISHED',
    false,
    'driver',
    'verify',
    'sms',
    0,
    '{"channel_name": "driver_sms"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00',
    'NEW',
    'PROCESSING',
    null
),
(   -- normal case of v2 sending logic
    '00000000000000000000000000000007',
    '22',
    '77',
    'group1',
    '//cmp_7_seg',
    '//cmp_7_seg_verification',
    'batch_22_77',
    'FINISHED',
    false,
    'driver',
    'testing',
    'push',
    0,
    '{"channel_name": "driver_push"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00',
    'NEW',
    'PROCESSING',
    'v2_scheduler'
);

drop table if exists crm_hub.batch_11_22;
create table crm_hub.batch_11_22(
    id INTEGER NOT NULL PRIMARY KEY,
    whatever text
);


drop table if exists crm_hub.batch_11_22_results;
create table crm_hub.batch_11_22_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    reason text,
    timestamp TIMESTAMP WITHOUT TIME ZONE,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER,
    timezone_name TEXT
);

insert into crm_hub.batch_11_22_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_1', 'driver_uuid_1', 'unique_driver_id_1', 'phone1', 'SUCCESS', '2020-10-01 05:06:07.111111'),
(2, 'db_id_2', 'driver_uuid_2', 'unique_driver_id_2', 'phone2', 'SUCCESS', '2020-10-01 05:06:07.111111'),
(3, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'FAIL', '2020-10-01 05:06:07.111111'),
(4, 'db_id_4', 'driver_uuid_4', 'unique_driver_id_4', 'phone4', 'FAIL', '2020-10-01 05:06:07.111111'),
(5, 'db_id_5', 'driver_uuid_5', 'unique_driver_id_5', 'phone5', 'SKIP', '2020-10-01 05:06:07.111111');

drop table if exists crm_hub.batch_33_44;
create table crm_hub.batch_33_44(
    id INTEGER NOT NULL PRIMARY KEY,
    whatever text
);


drop table if exists crm_hub.batch_33_44_results;
create table crm_hub.batch_33_44_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    reason text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_33_44_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'SUCCESS', '2020-10-02 05:06:07.111111');


drop table if exists crm_hub.batch_55_66;
create table crm_hub.batch_55_66(
    id INTEGER NOT NULL PRIMARY KEY,
    whatever text
);


drop table if exists crm_hub.batch_55_66_results;
create table crm_hub.batch_55_66_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    reason text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_55_66_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'SUCCESS', '2020-10-02 05:06:07.111111');


drop table if exists crm_hub.batch_77_88;
create table crm_hub.batch_77_88(
    id INTEGER NOT NULL PRIMARY KEY,
    whatever text
);


drop table if exists crm_hub.batch_77_88_results;
create table crm_hub.batch_77_88_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    reason text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_77_88_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'SUCCESS', '2020-10-02 05:06:07.111111');


drop table if exists crm_hub.batch_verify_1;
create table crm_hub.batch_verify_1(
    id INTEGER NOT NULL PRIMARY KEY,
    whatever text
);


drop table if exists crm_hub.batch_verify_1_results;
create table crm_hub.batch_verify_1_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    reason text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_verify_1_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'SUCCESS', '2020-10-02 05:06:07.111111');


drop table if exists crm_hub.batch_22_77;
create table crm_hub.batch_22_77(
    id INTEGER NOT NULL PRIMARY KEY,
    whatever text,
    another_whatever text,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    reason text,
    timestamp TIMESTAMP WITHOUT TIME ZONE,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER,
    timezone_name TEXT
);

insert into crm_hub.batch_22_77
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'SUCCESS', '2020-10-02 05:06:07.111111');

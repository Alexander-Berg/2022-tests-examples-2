-- == batch_sending == --
insert into crm_hub.batch_sending
(
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
    updated_at
)
values
(
    '00000000000000000000000000000001',
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
    '2020-09-15 14:00:00'
),
(
    '00000000000000000000000000000002',
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
    '2020-09-15 14:00:00'
),
(
    '00000000000000000000000000000003',
    '55',
    '66',
    '0_global_control',
    '//cmp_4_seg',
    '//cmp_4_seg_verification',
    'batch_55_66',
    'FINISHED',
    false,
    'driver',
    'testing',
    'push',
    0,
    '{"channel_name": "driver_push"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00'
),
(
    '00000000000000000000000000000004',
    '77',
    '88',
    '0_control',
    '//cmp_5_seg',
    '//cmp_5_seg_verification',
    'batch_77_88',
    'FINISHED',
    false,
    'driver',
    'testing',
    'push',
    0,
    '{"channel_name": "driver_push"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00'
),
(
    '00000000000000000000000000000005',
    '12',
    '21',
    '0_control',
    '//cmp_5_seg',
    '//cmp_5_seg_verification',
    'batch_12_21',
    'FINISHED',
    false,
    'driver',
    'testing',
    'legacywall',
    0,
    '{"channel_name": "driver_legacywall"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00'
);


-- == driver results tables == --
drop table if exists crm_hub.batch_11_22_results;
create table crm_hub.batch_11_22_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_11_22_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_1', 'driver_uuid_1', 'unique_driver_id_1', 'phone1', 'SUCCESS', '2020-10-01 05:06:07.111111'),
(2, 'db_id_2', 'driver_uuid_2', 'unique_driver_id_2', 'phone2', 'SUCCESS', '2020-10-01 05:06:07.111111'),
(3, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'FAIL', '2020-10-01 05:06:07.111111'),
(4, 'db_id_4', 'driver_uuid_4', 'unique_driver_id_4', 'phone4', 'FAIL', '2020-10-01 05:06:07.111111'),
(5, 'db_id_5', 'driver_uuid_5', 'unique_driver_id_5', 'phone5', 'SKIP', '2020-10-01 05:06:07.111111');


drop table if exists crm_hub.batch_33_44_results;
create table crm_hub.batch_33_44_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_33_44_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_3', 'driver_uuid_3', 'unique_driver_id_3', 'phone3', 'SUCCESS', '2020-10-02 05:06:07.111111');


drop table if exists crm_hub.batch_55_66_results;
create table crm_hub.batch_55_66_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_55_66_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_4', 'driver_uuid_4', 'unique_driver_id_4', 'phone4', 'SUCCESS', '2020-10-03 05:06:07.111111');


drop table if exists crm_hub.batch_77_88_results;
create table crm_hub.batch_77_88_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_77_88_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_5', 'driver_uuid_5', 'unique_driver_id_5', 'phone5', 'SUCCESS', '2020-10-04 05:06:07.111111');


drop table if exists crm_hub.batch_12_21_results;
create table crm_hub.batch_12_21_results(
    id INTEGER NOT NULL PRIMARY KEY,
    db_id text not null,
    driver_uuid text,
    unique_driver_id text,
    phone text,
    status text,
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

insert into crm_hub.batch_12_21_results
(id, db_id, driver_uuid, unique_driver_id, phone, status, timestamp)
values
(1, 'db_id_6', 'driver_uuid_6', 'unique_driver_id_6', 'phone6', 'SUCCESS', '2020-10-05 05:06:07.111111');

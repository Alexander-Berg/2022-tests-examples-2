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
    '123',
    '456',
    'group1',
    '//cmp_123_seg',
    '//cmp_123_seg_verification',
    'batch_123_456',
    'FINISHED',
    false,
    'user',
    'testing',
    'sms',
    0,
    '{"intent": "taxicrm_drivers", "sender": "go", "content": "content1", "channel_name": "user_sms"}',
    '{"report_group_id": "1_test", "group_name": "gr1"}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00'
);

-- == user results table == --
create table crm_hub.batch_123_456(
    id INTEGER NOT NULL PRIMARY KEY,
    user_id text not null,
    user_phone_id text,
    status text not null,
    reason text,
    timestamp TIMESTAMPTZ NOT NULL,
    experiment_type text not null,
    group_name text not null,
    group_id text not null,
    experiment_id text not null,
    was_logged BOOLEAN
);

insert into crm_hub.batch_123_456
(id, user_id, user_phone_id, status, reason, timestamp, experiment_type, group_name, group_id, experiment_id)
values
(1, 'uid_1', 'uphone_1', 'success', '', '2020-09-15 14:00:00', 'lavkaintaxi', 'gr1', '1_test', 'CRMSELFSERVICE-235'),
(2, 'uid_2', 'uphone_2', 'fail', 'policy', '2020-09-15 14:00:00', 'lavkaintaxi', 'gr1', '1_test', 'CRMSELFSERVICE-235'),
(3, 'uid_3', 'uphone_3', 'fail', 'policy', '2020-09-15 14:00:00', 'lavkaintaxi', 'gr1', '1_test', 'CRMSELFSERVICE-235'),
(4, 'uid_3', 'uphone_4', 'fail', 'policy', '2020-09-15 14:00:00', 'lavkaintaxi', 'gr1', '1_test', 'CRMSELFSERVICE-235'),
(5, 'uid_4', 'uphone_5', 'fail', 'policy', '2020-09-15 15:00:00', 'lavkaintaxi', 'gr1', '1_test', 'CRMSELFSERVICE-235');

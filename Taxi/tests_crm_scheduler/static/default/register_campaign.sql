INSERT INTO crm_scheduler.campaigns_info(campaign_id, group_id, channel_id, expire_time, update_timestamp, priority_id)
VALUES ('8a457abd-c10d-4450-a3ab-199f43ed44bc'::UUID, '0_testing', 1, NOW() + '3h'::interval, NOW(), 2);

INSERT INTO crm_scheduler.sendings(sending_id, campaign_id, group_id,
                                   policy_enabled, send_enabled, channel_id, size, dependency_uuid, priority_id,
                                   work_date_start, work_date_finish, work_time_start, work_time_finish,
                                   test_sending)
VALUES ('7d27b35a-0032-11ec-9a03-0242ac130003'::UUID, '8a457abd-c10d-4450-a3ab-199f43ed44bc'::UUID, '0_testing',
        True, True, 10, 12300, '8430b07a-0032-11ec-9a03-0242ac130003'::UUID, 2,
        NOW() - interval '1' day, NOW() + interval '1' day, 28800, 64800,
        False);

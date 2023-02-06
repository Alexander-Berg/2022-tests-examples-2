INSERT INTO crm_scheduler.campaigns_info(campaign_id, group_id, channel_id, expire_time, update_timestamp, priority_id)
VALUES ('123', '456', 1, NOW() + '3h'::interval, NOW(), 2);

INSERT INTO crm_scheduler.sendings( sending_id, campaign_id, group_id, policy_enabled, send_enabled
                                  , channel_id, size, dependency_uuid, priority_id, work_date_start
                                  , work_date_finish, work_time_start, work_time_finish, test_sending,
                                  generation_version, steps)
VALUES ('7d27b35a-0032-11ec-9a03-0242ac130003'::UUID, '123', '456', false, false, 10, 12300,
        '8430b07a-0032-11ec-9a03-0242ac130003'::UUID, 2, '2021-12-01T10:00:00Z', '2021-12-03T10:00:00Z', 28800, 64800,
        false, 3, '{crm_policy, counter_filter, promo, driver_wall, logs}');

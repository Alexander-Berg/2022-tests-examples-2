INSERT INTO crm_scheduler.sendings(sending_id, campaign_id, group_id, policy_enabled, send_enabled, channel_id, size,
                                   dependency_uuid, priority_id, last_policy_generated, work_date_start,
                                   work_date_finish, work_time_start, work_time_finish, test_sending)
VALUES ('7d27b35a-0032-11ec-9a03-0242ac130003'::UUID, '8a457abd-c10d-4450-a3ab-199f43ed44bc'::UUID, '0_testing', True,
        True, 10, 3300, '8430b07a-0032-11ec-9a03-0242ac130003'::UUID, 2, 3300, NOW() - interval '1' day,
        NOW() + interval '1' day, 28800, 64800, false);

UPDATE crm_scheduler.sendings_runtime
SET size                    = 3300
  , policy_summ_success     = 3200
  , policy_summ_failed      = 100
  , policy_fail_messages    = '{error_test1}'
  , send_to_channel_success = 1237
  , send_to_channel_failed  = 10
  , send_fail_messages      = '{error_test2}'
  , logs_success            = 3200
  , logs_failed             = 100
  , logs_fail_messages      = '{error_test3}'
  , sending_started         = NOW()
  , finish_task_generated   = False
WHERE sending_id_id = 1;

INSERT INTO crm_scheduler.sendings(sending_id, campaign_id, group_id, policy_enabled, send_enabled, channel_id, size,
                                   dependency_uuid, priority_id, last_policy_generated, work_date_start,
                                   work_date_finish, work_time_start, work_time_finish, test_sending)
VALUES ('7d27b35a-0032-11ec-9a03-0242ac130003'::UUID, '8a457abd-c10d-4450-a3ab-199f43ed44bc'::UUID, '0_testing', True,
        True, 10, 3300, '8430b07a-0032-11ec-9a03-0242ac130003'::UUID, 2, 3300, NOW() - interval '1' day,
        NOW() + interval '1' day, 28800, 64800, false);

INSERT INTO crm_scheduler.task_pool_sending_finished ( id, sending_id
                                                     , successfull, error
                                                     , error_details, task_received
                                                     , retry_count, time_runned
                                                     , access_thread_id)
VALUES (1015, '7d27b35a-0032-11ec-9a03-0242ac130003'::UUID, True, NULL, '{}', True, 0, NOW(), 57);


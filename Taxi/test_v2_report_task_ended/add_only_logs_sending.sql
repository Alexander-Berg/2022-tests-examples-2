INSERT INTO crm_scheduler.sendings (campaign_id, group_id, policy_enabled, send_enabled, channel_id, size, dependency_uuid, priority_id, last_first_step_generated, sending_id, last_send_generated, last_log_generated, is_active, time_stopped, generation_version, steps, work_date_start,
                                    work_date_finish, work_time_start, work_time_finish, test_sending)
    VALUES('company_id_1', '1_testings', false, false, -1, 1230,
           '8430b07a-0032-11ec-9a03-0242ac130003'::UUID, 2, 1230,
           '7d27b35a-0032-11ec-9a03-0242ac130003'::UUID, 0,0,true,NULL,3,'{logs}',
           '2021-12-20 0:0:0', '2022-12-20 0:0:0', 0, 86399, false);

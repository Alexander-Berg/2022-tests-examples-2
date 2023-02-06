INSERT INTO crm_scheduler.task_pool_crm_policy(sending_id_id, scope_start, scope_end, start_offset, size)
    VALUES(1, '{1}', '{2}','{0}', '{2}');
INSERT INTO crm_scheduler.task_pool_crm_policy_in_process(id, sending_id_id, scope_start, scope_end, start_offset, size, time_runned, access_thread_id, retry_count)
    VALUES(32, 1, '{1}', '{2}','{0}', '{2}', NOW(), 1, 0);

INSERT INTO crm_scheduler.task_pool_user_push(sending_id_id, scope_start, scope_end, start_offset, size)
    VALUES(1, '{1}', '{2}','{0}', '{2}');
INSERT INTO crm_scheduler.task_pool_user_push_in_process(id, sending_id_id, scope_start, scope_end, start_offset, size, time_runned, access_thread_id, retry_count)
    VALUES(43, 1, '{1}', '{2}','{0}', '{2}', NOW(), 1, 0);

INSERT INTO crm_scheduler.task_pool_logs(sending_id_id, scope_start, scope_end, start_offset, size)
    VALUES(1, '{1}', '{2}','{0}', '{2}');
INSERT INTO crm_scheduler.task_pool_logs_in_process(id, sending_id_id, scope_start, scope_end, start_offset, size, time_runned, access_thread_id, retry_count)
    VALUES(12, 1, '{1}', '{2}','{0}', '{2}', NOW(), 1, 0);


INSERT INTO crm_scheduler.task_reported_default (sending_id_id , scope_start, scope_end, start_offset
                                        , size, last_job_task_type_id, payload_int, time_reported
                                        , channel_to_send_name, processed)
                                    VALUES(1, '{1}', '{12}', '{0}', '{12}', 1, 100, NOW(), 'user_push', -1);

INSERT INTO crm_scheduler.task_reported_default (sending_id_id , scope_start, scope_end, start_offset
                                                , size, last_job_task_type_id, payload_int, time_reported
                                                , channel_to_send_name, processed)
                                    VALUES(1, '{1}', '{12}', '{0}', '{12}', 13, 100, NOW(), 'user_push', -1);

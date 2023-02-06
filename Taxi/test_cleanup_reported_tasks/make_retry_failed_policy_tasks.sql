INSERT INTO crm_scheduler.task_pool_crm_policy_in_process (id, sending_id_id, scope_start, scope_end, start_offset, size, time_runned, retry_count, access_thread_id)
VALUES(1111, 1, '{4001}','{4400}','{0}', '{400}', NOW() - '100 hour'::interval, 1000,13);

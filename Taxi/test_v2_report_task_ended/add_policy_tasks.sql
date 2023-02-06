INSERT INTO crm_scheduler.task_pool_crm_policy_in_process(id, sending_id_id, scope_start, scope_end, start_offset, size, retry_count, time_runned, step_num, source_task_ids,  access_thread_id)
    VALUES  (1000, 1, '{1}'   , '{400}' , '{0}', '{400}', 0, NOW(), 1, '{}',321)
          , (1001, 1, '{401}' , '{800}' , '{0}', '{400}', 0, NOW(), 1, '{}',321)
          , (1002, 1, '{801}' , '{1200}', '{0}', '{400}', 0, NOW(), 1, '{}',321)
          , (1003, 1, '{1201}', '{1230}', '{0}', '{400}', 0, NOW(), 1, '{}',321);

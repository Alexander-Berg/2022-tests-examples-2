INSERT INTO crm_scheduler.task_pool_driver_wall_in_process(id, sending_id_id, scope_start, scope_end, start_offset, size, retry_count, time_runned, step_num, source_task_ids,  access_thread_id)
    VALUES  (1000, 1, '{1}'   , '{1000}' , '{0}', '{1000}', 0, NOW(), 1, '{}',321)
          , (1001, 1, '{1001}' , '{1230}' , '{0}', '{230}', 0, NOW(), 1, '{}',321);

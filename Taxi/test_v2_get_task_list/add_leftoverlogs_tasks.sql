INSERT INTO crm_scheduler.task_pool_logs(sending_id_id, scope_start, scope_end, start_offset, size, retry_count, task_ids_to_log, time_generated, step_num, source_task_ids)
    VALUES  (1, '{}', '{}' , '{}', '{}', 0, '{1000,1001,1002}', NOW(), 4, '{}')
          , (1, '{}', '{}' , '{}', '{}', 0, '{1003}', NOW(), 4, '{}');

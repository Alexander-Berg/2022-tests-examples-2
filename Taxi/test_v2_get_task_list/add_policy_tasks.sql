INSERT INTO crm_scheduler.task_pool_crm_policy(sending_id_id, scope_start, scope_end, start_offset, size, retry_count, time_generated, step_num, source_task_ids)
    VALUES  (1, '{1}'   , '{400}' , '{0}', '{400}', 0, NOW(), 1, '{}')
          , (1, '{401}' , '{800}' , '{0}', '{400}', 0, NOW(), 1, '{}')
          , (1, '{801}' , '{1200}', '{0}', '{400}', 0, NOW(), 1, '{}')
          , (1, '{1201}', '{1230}', '{0}', '{400}', 0, NOW(), 1, '{}');

INSERT INTO crm_scheduler.task_reported_default(id, sending_id_id, scope_start, scope_end, start_offset, size
                                        , last_job_task_type_id, payload_int, time_reported, channel_to_send_name
                                        , processed, logs_generated, step_num, filter_approved )
    VALUES  (1000, 1, '{1}', '{4300}', '{0}', '{4300}', 1, 0, NOW(), NULL,0,false, 1, 3567)
            ,(1001, 1, '{4301}', '{8002}', '{0}', '{400}', 1, 0, NOW(), NULL,0,false, 1, 3314);

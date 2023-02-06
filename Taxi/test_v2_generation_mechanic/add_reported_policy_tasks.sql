INSERT INTO crm_scheduler.task_reported_default(id, sending_id_id, scope_start, scope_end, start_offset, size
                                        , last_job_task_type_id, payload_int, time_reported, channel_to_send_name
                                        , processed, logs_generated, step_num, filter_approved )
    VALUES  (1000, 1, '{1}', '{400}', '{0}', '{400}', 1, 0, NOW(), NULL,0,false, 1, 123)
            ,(1001, 1, '{401}', '{800}', '{0}', '{400}', 1, 0, NOW(), NULL,0,false, 1, 398)
            ,(1002, 1, '{801}', '{1200}', '{0}', '{400}', 1, 0, NOW(), NULL,0,false, 1, 212)
            ,(1003, 1, '{1201}', '{1600}', '{0}', '{400}', 1, 0, NOW(), NULL,0,false, 1, 400);

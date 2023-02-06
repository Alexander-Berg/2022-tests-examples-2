INSERT INTO crm_scheduler.task_reported_default(id, sending_id_id, scope_start, scope_end, start_offset, size
                                               , last_job_task_type_id, payload_int, time_reported, channel_to_send_name
                                               , processed, logs_generated, step_num, filter_approved )
VALUES  (1004, 1, '{}', '{}', '{0}', '{1000}', 10, 0, NOW(), NULL,0,false, 3, 1000)
     ,(1005, 1, '{}', '{}', '{0}', '{133}', 10, 0, NOW(), NULL,0,false, 3, 133);

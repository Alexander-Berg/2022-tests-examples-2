ALTER TABLE form_builder.partial_request_queue DROP CONSTRAINT partial_request_queue_form_code_stage_num_submit_id_key;

CREATE UNIQUE INDEX partial_request_queue_form_code_stage_num_submit_id_key
    ON form_builder.partial_request_queue(form_code, stage_num, submit_id)
    WHERE status = 'PENDING' OR status = 'SUBMITTED';

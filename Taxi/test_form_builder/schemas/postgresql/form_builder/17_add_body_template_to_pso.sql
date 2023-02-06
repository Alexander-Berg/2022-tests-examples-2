ALTER TABLE form_builder.partial_submit_options
    ADD COLUMN body_template TEXT
;
ALTER TABLE form_builder.partial_request_queue
    ADD COLUMN body_template TEXT
;

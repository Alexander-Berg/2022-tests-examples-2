ALTER TABLE form_builder.partial_submit_options
    ADD COLUMN headers form_builder.submit_header[];
ALTER TABLE form_builder.partial_request_queue
    ADD COLUMN headers form_builder.submit_header[];

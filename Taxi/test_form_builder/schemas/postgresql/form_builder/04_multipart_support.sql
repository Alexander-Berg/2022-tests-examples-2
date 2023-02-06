ALTER TABLE form_builder.submit_options
    ADD COLUMN is_multipart BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE form_builder.request_queue
    ADD COLUMN is_multipart BOOLEAN NOT NULL DEFAULT FALSE;

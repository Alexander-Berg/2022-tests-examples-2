ALTER TABLE form_builder.responses ADD COLUMN submit_id TEXT;

CREATE UNIQUE INDEX form_builder_responses_form_code_submit_id_uniq_idx
    ON form_builder.responses (form_code, submit_id)
    WHERE submit_id IS NOT NULL;

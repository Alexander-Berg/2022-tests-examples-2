CREATE TABLE form_builder.async_validation_states (
    form_code TEXT REFERENCES form_builder.forms(code) NOT NULL,
    field_code TEXT /* REFERENCES form_builder.fields(code) */ NOT NULL,
    submit_id TEXT NOT NULL,

    value JSONB NOT NULL, -- row value from form
    is_sent BOOLEAN NOT NULL,  -- marks, if verification submit sent
    is_valid BOOLEAN  -- marks, if verification passed or not. if NULL - verification still not processed (user didn't pass data at all)
);

CREATE UNIQUE INDEX uniq_form_builder_async_validation_states_idx
    ON form_builder.async_validation_states(form_code, field_code, submit_id);

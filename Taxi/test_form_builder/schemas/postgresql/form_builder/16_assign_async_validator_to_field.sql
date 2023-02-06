CREATE TYPE form_builder.async_validator_t AS (
    async_validator TEXT,  -- validator implementation name
    validate_for TEXT  -- field for what validator is used
);

ALTER TABLE form_builder.fields
    ADD COLUMN async_validator form_builder.async_validator_t
;

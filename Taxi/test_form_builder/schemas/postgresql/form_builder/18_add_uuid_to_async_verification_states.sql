ALTER TABLE form_builder.async_validation_states
    ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
-- default '' is bad hack, temporary thing. MUST BE DELETED

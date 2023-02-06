CREATE TYPE form_builder.external_source_t AS (
    external_suggest TEXT,
    suggest_from TEXT,
    inline_from TEXT,
    refuse_edit_after_inline BOOLEAN
);

ALTER TABLE form_builder.fields
    ADD COLUMN external_source form_builder.external_source_t
;

CREATE TYPE form_builder.needed_authorization_t AS (
    passport BOOLEAN,
    opteum BOOLEAN
);

ALTER TABLE form_builder.forms
    ADD COLUMN needed_authorization form_builder.needed_authorization_t
        DEFAULT (FALSE, FALSE)::form_builder.needed_authorization_t;

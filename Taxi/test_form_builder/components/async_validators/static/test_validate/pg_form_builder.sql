INSERT INTO form_builder.field_templates
    (name, is_array, has_choices, tags, author)
VALUES
    ('tst', FALSE, FALSE, array[]::text[], 'd1mbas')
;

INSERT INTO form_builder.forms
    (code, conditions, default_locale, supported_locales, author)
VALUES
    ('tst_form', '{}'::jsonb, '', array[]::text[], 'd1mbas')
;

INSERT INTO form_builder.stages
    (form_code)
VALUES
    ('tst_form')
;

INSERT INTO form_builder.fields
    (code, visible)
VALUES
    ('tst-field', TRUE)
;

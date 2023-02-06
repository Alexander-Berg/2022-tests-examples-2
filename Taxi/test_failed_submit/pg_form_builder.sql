INSERT INTO form_builder.field_templates (
    id,
    name,
    value_type,
    is_array,
    has_choices,
    tags,
    personal_data_type,
    default_label,
    regex_pattern,
    default_choices,
    author
)
VALUES
(
    1,
    'phone_pd',
    'string',
    False,
    False,
    '{}'::TEXT[],
    'phones',
    ('', 't')::form_builder.translatable,
    '',
    NULL,
    'testsuite'
)
;

INSERT INTO form_builder.forms (code, conditions, author, default_locale, supported_locales)
VALUES
(
    'form_1',
    '{}'::JSONB,
    'testsuite',
    'ru',
    '{"ru", "en"}'::TEXT[]
)
;

INSERT INTO form_builder.stages (id, form_code)
VALUES (1, 'form_1');

INSERT INTO form_builder.fields (
    id,
    stage_id,
    code,
    template_id,
    visible,
    obligatory,
    async_validator
)
VALUES
(
    1,
    1,
    'user_phone',
    1,
    TRUE,
    TRUE,
    ('sms_validator', 'user_phone')
)
;

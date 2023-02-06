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
) VALUES (
    1,
    'email',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    'emails',
    ('', 'e-mail')::form_builder.translatable,
    '^\S+@\S+$',
    NULL,
    'nevladov'
),
(
    2,
    '1-3',
    'integer',
    FALSE,
    TRUE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    '',
    ARRAY[
        ('{"type": "integer", "integerValue": 1}'::JSONB, ('', '1')::form_builder.translatable),
        ('{"type": "integer", "integerValue": 1}'::JSONB, ('', '2')::form_builder.translatable),
        ('{"type": "integer", "integerValue": 1}'::JSONB, ('', '3')::form_builder.translatable)
    ]::form_builder.choice[],
    'nevladov'
),
(
    3,
    '1-3_no_choices',
    'integer',
    FALSE,
    TRUE,
    '{}'::TEXT[],
    NULL,
    NULL,
    '',
    NULL,
    'nevladov'
),
(
    4,
    'Caption',
    NULL,
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    NULL,
    '',
    NULL,
    'nevladov'
);

INSERT INTO form_builder.forms (
    code,
    conditions,
    author,
    default_locale,
    supported_locales
) VALUES (
    'form_1',
    '{"cond_1": {"$ne": {"type": "string", "stringValue": "nevladov@yandex.ru"}}}'::JSONB,
    'nevladov',
    'ru',
    '{"ru", "en"}'::TEXT[]
),
(
    'form_2',
    '{"cond_1": {"$ne": {"type": "string", "stringValue": "nevladov@yandex.ru"}}}'::JSONB,
    'nevladov',
    'ru',
    '{"ru", "en"}'::TEXT[]
);

INSERT INTO form_builder.stages (
    form_code
) VALUES (
    'form_1'
);

INSERT INTO form_builder.fields (
    stage_id,
    code,
    template_id,
    visible,
    obligatory,
    default_value,
    label,
    obligation_condition,
    visibility_condition
) VALUES (
    1,
    'driver_email',
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'e-mail водителя')::form_builder.translatable,
    'cond_1',
    NULL
);

INSERT INTO form_builder.responses (
    form_code
) VALUES (
    'form_2'
);

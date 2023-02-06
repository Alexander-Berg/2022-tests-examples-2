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
    author
) VALUES (
    1,
    'string_template',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    'emails',
    ('', 'e-mail')::form_builder.translatable,
    '^\S+@\S+$',
    'nevladov'
),
(
    2,
    'datetime_template',
    'datetime',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    NULL,
    NULL,
    'd1mbas'
)
;

INSERT INTO form_builder.forms (
    code,
    title,
    description,
    conditions,
    author,
    default_locale,
    supported_locales,
    ya_metric_counter
) VALUES (
    'form_1',
    ('', 'x')::form_builder.translatable,
    ('', 'x')::form_builder.translatable,
    '{"cond_1": {"driver_email": {"$ne": {"type": "string", "stringValue": "nevladov@yandex.ru"}}}}'::JSONB,
    'nevladov',
    'ru',
    '{"en", "ge"}'::TEXT[],
    NULL
),
(
    'form_2',
    ('', 'x')::form_builder.translatable,
    ('', 'x')::form_builder.translatable,
    '{"cond_1": {"driver_email": {"$ne": {"type": "string", "stringValue": "nevladov@yandex.ru"}}}}'::JSONB,
    'nevladov',
    'ru',
    '{"en", "ge"}'::TEXT[],
    123
);

INSERT INTO form_builder.stages (
    id,
    form_code,
    title,
    description
) VALUES (
    1,
    'form_1',
    ('', 'x')::form_builder.translatable,
    ('', 'x')::form_builder.translatable
),
(
    2,
    'form_2',
    ('', 'x')::form_builder.translatable,
    ('', 'x')::form_builder.translatable
);

INSERT INTO form_builder.fields (
    id,
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
    1,
    'driver_email',
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'e-mail водителя')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    2,
    1,
    'park_email',
    1,
    TRUE,
    TRUE,
    NULL,
    ('x.y', '')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    5,
    1,
    'registration_date',
    2,
    TRUE,
    FALSE,
    '{"type": "datetime", "datetimeValue": "2020-09-09T19:09:00+03:00"}',
    ('', 'Дата регистрации')::form_builder.translatable,
    NULL,
    NULL
),
(
    3,
    2,
    'driver_email',
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'e-mail водителя')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    4,
    2,
    'park_email',
    1,
    TRUE,
    TRUE,
    NULL,
    ('x.y', '')::form_builder.translatable,
    'cond_1',
    NULL
);

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
    'field_template_1',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    'emails',
    ('', 'e-mail')::form_builder.translatable,
    '^\S+@\S+$',
    NULL,
    'author_1'
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
    NULL,
    'd1mbas'
)
;

INSERT INTO form_builder.forms (
    id,
    author,
    created,
    code,
    conditions,
    default_locale,
    supported_locales
) VALUES (
    100,
    'author_1',
    '2020-03-11 13:00:00+3',
    'form_1',
    '{"cond_1": {"driver_email": {"$ne": {"type": "string", "stringValue": "nevladov@yandex.ru"}}}}'::JSONB,
    'ru',
    '{"ru", "en"}'::TEXT[]
),
(
    101,
    'author_2',
    '2020-03-11 13:00:00+3',
    'form_2',
    '{"cond_1": {"driver_email": {"$ne": {"type": "string", "stringValue": "nevladov@yandex.ru"}}}}'::JSONB,
    'ru',
    '{"ru", "en"}'::TEXT[]
);

INSERT INTO form_builder.stages (
    id,
    form_code
) VALUES (
    1,
    'form_1'
),
(
    2,
    'form_1'
),
(
    3,
    'form_2'
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
    'field_1',
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
    'field_2',
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'e-mail водителя')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    3,
    1,
    'field_3',
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
    1,
    'field_4',
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'e-mail водителя')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    5,
    2,
    'field_5',
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'e-mail водителя')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    6,
    3,
    'field_6',
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'e-mail водителя')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    7,
    3,
    NULL,
    1,
    TRUE,
    TRUE,
    NULL,
    ('', 'label')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    8,
    1,
    NULL,
    2,
    TRUE,
    TRUE,
    '{"type": "datetime", "datetimeValue": "2020-09-09T19:09:00+03:00"}',
    ('', 'label')::form_builder.translatable,
    'cond_1',
    NULL
)
;

INSERT INTO form_builder.submit_limits (form_code, field_code, max_count)
VALUES ('form_1', 'field_1', 100500),
       ('form_2', 'field_2', 250)
;

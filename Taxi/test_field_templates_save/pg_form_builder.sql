INSERT INTO form_builder.field_templates (
    id,
    name,
    value_type,
    personal_data_type,
    is_array,
    has_choices,
    tags,
    default_label,
    regex_pattern,
    default_choices,
    author
) VALUES (
    1,
    'Электронная почта',
    'string',
    'emails',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    ('', 'e-mail')::form_builder.translatable,
    '^\S+@\S+$',
    NULL,
    'nevladov'
);

SELECT setval('form_builder.field_templates_id_seq', 2, FALSE);

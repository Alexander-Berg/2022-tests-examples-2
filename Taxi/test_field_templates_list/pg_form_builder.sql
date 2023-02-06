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
    100,
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
    101,
    'field_template_2',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    'emails',
    ('', 'e-mail')::form_builder.translatable,
    '^\S+@\S+$',
    NULL,
    'author_2'
);

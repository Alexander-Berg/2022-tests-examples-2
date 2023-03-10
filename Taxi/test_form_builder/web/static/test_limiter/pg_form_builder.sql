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
) VALUES
(
    1,
    'field_template_1',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    NULL,
    NULL,
    NULL,
    'd1mbas'
),
(
    2,
    'field_template_2',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    'identifications',
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    'd1mbas'
),
(
    3,
    'field_template_1',
    'integer',
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

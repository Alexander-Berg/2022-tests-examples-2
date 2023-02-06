INSERT INTO form_builder.field_templates (
    id,
    name,
    value_type,
    is_array,
    has_choices,
    tags,
    personal_data_type,
    author
) VALUES
(
    1,
    'string_template',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    'd1mbas'
),
(
    2,
    'string_template',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    'phones',
    'd1mbas'
),
(
    3,
    'file_template',
    'file',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    'd1mbas'
),
(
    4,
    'dt_template',
    'datetime',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    'd1mbas'
),
(
    5,
    'array_template',
    'string',
    TRUE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    'd1mbas'
),
(
    6,
    'number_template',
    'number',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    'd1mbas'
),
(
    7,
    'numbers_array',
    'number',
    TRUE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    'd1mbas'
)
;

INSERT INTO form_builder.forms (
    code,
    conditions,
    author,
    default_locale,
    supported_locales
) VALUES
(
    'form_1',
    '{}'::JSONB,
    'd1mbas',
    'ru',
    '{"ru", "en"}'::TEXT[]
);

INSERT INTO form_builder.submit_options (
    form_code,
    method,
    url,
    headers,
    tvm_service_id,
    body_template,
    is_multipart
) VALUES
(
    'form_1',
    'POST',
    'http://form-builder.taxi.yandex.net',
    '{}'::form_builder.submit_header[],
    '12345',
    '{"field_1": {{ field_1 }}, "field_2": {{ field_2}} }',
    TRUE
)
;

INSERT INTO form_builder.stages (
    id,
    form_code
) VALUES
(
    1,
    'form_1'
),
(
    2,
    'form_1'
);

INSERT INTO form_builder.fields (
    id,
    stage_id,
    code,
    template_id,
    visible,
    label,
    obligatory,
    external_source
)
VALUES
(
    1,
    1,
    'field_1',
    1,
    TRUE,
    ('', 't')::form_builder.translatable,
    TRUE,
    ('geo_suggests_city', NULL, 'name', TRUE, NULL)::form_builder.external_source_t
)
;

INSERT INTO form_builder.fields (
    id,
    stage_id,
    code,
    template_id,
    visible,
    label,
    obligatory
) VALUES
(
    3,
    1,
    'file_field',
    3,
    TRUE,
    ('', 't')::form_builder.translatable,
    FALSE
),
(
    4,
    1,
    'dt_field',
    4,
    TRUE,
    ('', 't')::form_builder.translatable,
    FALSE
),
(
    5,
    2,
    'array_field',
    5,
    TRUE,
    ('', 't')::form_builder.translatable,
    FALSE
),
(
    6,
    2,
    'number_field',
    6,
    TRUE,
    ('', 't')::form_builder.translatable,
    FALSE
),
(
    7,
    2,
    'numbers_field',
    7,
    TRUE,
    ('', 't')::form_builder.translatable,
    FALSE
)
;

INSERT INTO form_builder.fields (
    id,
    stage_id,
    code,
    template_id,
    visible,
    label,
    obligatory,
    async_validator
)
VALUES
    (
        2,
        1,
        'field_2',
        2,
        TRUE,
        ('', 't')::form_builder.translatable,
        TRUE,
        ('sms_validator', 'field_2')
    )
;

INSERT INTO form_builder.async_validation_states
    (form_code, field_code, submit_id, is_sent, is_valid, value, uuid)
VALUES
    ('form_1', 'field_2', 'verification-fail', TRUE, FALSE, '{"type": "string", "stringValue": "A"}', 'uuid1'),
    ('form_1', 'field_2', 'verification-not-sent', TRUE, NULL, '{"type": "string", "stringValue": "A"}', 'uuid2')
;

INSERT INTO form_builder.responses (form_code, submit_id)
VALUES ('form_1', 'abc'),
       ('form_1', 'abd')
;

INSERT INTO form_builder.response_values (response_id, key, value, is_array, personal_data_type)
VALUES (1, 'field_1', '{"type": "string", "stringValue": "abc"}', FALSE, NULL),
       (1, 'field_2', '{"type": "string", "stringValue": "personal_id_1"}', FALSE, 'phones'),
       (2, 'field_1', '{"type": "string", "stringValue": "abc"}', FALSE, NULL)
;

INSERT INTO caches.geodata_regions (id, parent_id, country_id, population, region_type, last_updated_ts)
VALUES (1, NULL, NULL, 100, 1, 0)
;

INSERT INTO caches.geodata_localized_names (real_name, lower_name, lang, region_id)
VALUES ('value_1', 'value_1', 'en', 1)
;

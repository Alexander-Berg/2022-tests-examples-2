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
    3,
    'test_case_template',
    'integer',
    FALSE,
    TRUE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    '',
    ARRAY[
        ('{"type": "integer", "integerValue": 1}'::JSONB, ('', '1')::form_builder.translatable),
        ('{"type": "integer", "integerValue": 2}'::JSONB, ('', '2')::form_builder.translatable),
        ('{"type": "integer", "integerValue": 3}'::JSONB, ('', '3')::form_builder.translatable),
        ('{"type": "integer", "integerValue": 4}'::JSONB, ('', '4')::form_builder.translatable),
        ('{"type": "integer", "integerValue": 5}'::JSONB, ('', '5')::form_builder.translatable),
        ('{"type": "integer", "integerValue": 6}'::JSONB, ('', '5')::form_builder.translatable)
    ]::form_builder.choice[],
    'nevladov'
),
(
    1,
    'field_template_1',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    'identifications',
    NULL,
    '^\w+$',
    NULL,
    'nevladov'
),
(
    2,
    'field_template_2',
    'datetime',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    'nevladov'
),
(
    4,
    'field_template_4',
    'string',
    TRUE,
    FALSE,
    '{}'::TEXT[],
    'identifications',
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    'nevladov'
),
(
    5,
    'multiselect_template_with_default',
    'string',
    TRUE,
    TRUE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    ARRAY[
        ('{"type": "string", "stringValue": "A"}'::JSONB, ('', '1')::form_builder.translatable),
        ('{"type": "string", "stringValue": "B"}'::JSONB, ('', '2')::form_builder.translatable)
    ]::form_builder.choice[],
    'd1mbas'
),
(
    6,
    'multiselect_template_no_default',
    'string',
    TRUE,
    TRUE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    'd1mbas'
),
(
    7,
    'number_template',
    'number',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    'd1mbas'
),
(
    8,
    'string_template',
    'string',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    'd1mbas'
),
(
    9,
    'integer_template',
    'integer',
    FALSE,
    FALSE,
    '{}'::TEXT[],
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
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
    ('{"cond_1": {"test_case": {"$eq": {"type": "integer", "integerValue": 1}}}, ' ||
     '"cond_2": {"test_case": {"$ne": {"type": "integer", "integerValue": 2}}}, ' ||
     '"cond_3": {"test_case": {"$in": [{"type": "integer", "integerValue": 3}, {"type": "integer", "integerValue": 4}]}}, ' ||
     '"cond_4": {"test_case": {"$nin": [{"type": "integer", "integerValue": 5}, {"type": "integer", "integerValue": 6}]}}}')::JSONB,
    'nevladov',
    'ru',
    '{"ru", "en"}'::TEXT[]
),
(
'form_3', '{}'::JSONB, 'd1mbas', 'ru', '{"ru", "en"}'::TEXT[]
);

INSERT INTO form_builder.submit_options (
    form_code,
    method,
    url,
    headers,
    tvm_service_id,
    body_template,
    host,
    port,
    is_multipart
) VALUES
(
    'form_1',
    'POST',
    'http://form-builder.taxi.yandex.net',
    ARRAY[
        ('test1', 'test1')::form_builder.submit_header,
        ('test1', 'test2')::form_builder.submit_header
    ]::form_builder.submit_header[],
    '12345',
    '{{ test_case }}',
    'form-builder.taxi.yandex.net',
    80,
    FALSE
),
(
    'form_1',
    'PUT',
    'http://form-builder.taxi.yandex.net',
    ARRAY[
        ('test1', 'test1')::form_builder.submit_header,
        ('test1', 'test2')::form_builder.submit_header
    ]::form_builder.submit_header[],
    '12345',
    '{{ test_case }}',
    'form-builder.taxi.yandex.net',
    80,
    FALSE
);

INSERT INTO form_builder.stages (
    id,
    form_code
) VALUES
(
    1,
    'form_1'
),
(2, 'form_3')
;

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
) VALUES
(
    0,
    1,
    'test_case',
    3,
    TRUE,
    TRUE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL
),
(
    1,
    1,
    'field_1',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    'cond_1',
    NULL
),
(
    2,
    1,
    'field_2',
    2,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    'cond_2',
    NULL
),
(
    3,
    1,
    'field_3',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    'cond_3',
    NULL
),
(
    4,
    1,
    'field_4',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    'cond_4',
    NULL
),
(
    5,
    1,
    'field_5',
    4,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL
),
(
    6,
    1,
    'number_field',
    7,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL
);

INSERT INTO form_builder.fields (
    id,
    stage_id,
    code,
    template_id,
    visible,
    default_value,
    choices
)
VALUES
(
    11,
    1,
    'multiselect_with_template_default',
    5,
    TRUE,
    NULL,
    NULL
),
(
     12,
    1,
    'multiselect_with_template_default_and_value_default',
    5,
    TRUE,
    '{"type": "array", "arrayValue": [{"type": "string", "stringValue": "A"}]}'::JSONB,
    NULL
),
(
    13,
    1,
    'multiselect_with_template_default_and_self',
    5,
    TRUE,
    NULL,
    ARRAY [
        ('{"type": "string", "stringValue": "C"}'::JSONB, ('', '1')::form_builder.translatable),
        ('{"type": "string", "stringValue": "D"}'::JSONB, ('', '1')::form_builder.translatable)
    ]::form_builder.choice[]
),
(
    14,
    1,
    'multiselect_with_template_default_and_self_and_value_default',
    5,
    TRUE,
    '{"type": "array", "arrayValue": [{"type": "string", "stringValue": "C"}]}'::JSONB,
    ARRAY [
        ('{"type": "string", "stringValue": "C"}'::JSONB, ('', '1')::form_builder.translatable),
        ('{"type": "string", "stringValue": "D"}'::JSONB, ('', '1')::form_builder.translatable)
    ]::form_builder.choice[]
),
(
    21,
    1,
    'multiselect_with_no_default',
    6,
    TRUE,
    NULL,
    ARRAY [
        ('{"type": "string", "stringValue": "A"}'::JSONB, ('', '1')::form_builder.translatable),
        ('{"type": "string", "stringValue": "B"}'::JSONB, ('', '1')::form_builder.translatable)
    ]::form_builder.choice[]
),
(
    22,
    1,
    'multiselect_with_self_default',
    6,
    TRUE,
    '{"type": "array", "arrayValue": [{"type": "string", "stringValue": "A"}]}'::JSONB,
    ARRAY [
        ('{"type": "string", "stringValue": "A"}'::JSONB, ('', '1')::form_builder.translatable),
        ('{"type": "string", "stringValue": "B"}'::JSONB, ('', '1')::form_builder.translatable)
    ]::form_builder.choice[]
)
;

INSERT INTO form_builder.fields (
    id,
    stage_id,
    code,
    template_id,
    visible,
    label,
    external_source
)
VALUES
(
    30,
    2,
    'suggest_source',
    8,
    TRUE,
    ('', 't')::form_builder.translatable,
    ('dadata_suggests', NULL, 'data.inn', TRUE, NULL)::form_builder.external_source_t
),
(
    31,
    2,
    'suggest_dependent_non_editable',
    8,
    TRUE,
    ('', 't')::form_builder.translatable,
    (NULL, 'suggest_source', 'data.kpp', TRUE, NULL)::form_builder.external_source_t
),
(
    32,
    2,
    'suggest_dependent_editable',
    8,
    TRUE,
    ('', 't')::form_builder.translatable,
    (NULL, 'suggest_source', 'data.ogrn', FALSE, NULL)::form_builder.external_source_t
),
(
    33,
    2,
    'suggest_dependent_non_editable_2',
    2,
    TRUE,
    ('', 't')::form_builder.translatable,
    (NULL, 'suggest_source', 'data.state.registration_date', TRUE, NULL)::form_builder.external_source_t
),
(
    40,
    2,
    'geosuggest_source',
    8,
    TRUE,
    ('', 't')::form_builder.translatable,
    ('geo_suggests_city', NULL, 'name', TRUE, NULL)::form_builder.external_source_t
),
(
    41,
    2,
    'geosuggest_dependent_non_editable',
    9,
    TRUE,
    ('', 't')::form_builder.translatable,
    (NULL, 'geosuggest_source', 'region_id', TRUE, NULL)::form_builder.external_source_t
)
;

INSERT INTO caches.geodata_regions (id, parent_id, country_id, population, region_type, last_updated_ts)
VALUES (1, NULL, NULL, 100, 1, 0),
       (3, NULL, 1, 100, 1, 0)
;

INSERT INTO caches.geodata_localized_names (real_name, lower_name, lang, region_id)
VALUES ('Moscow', 'moscow', 'en', 3),
       ('Москва', 'москва', 'ru', 3)
;

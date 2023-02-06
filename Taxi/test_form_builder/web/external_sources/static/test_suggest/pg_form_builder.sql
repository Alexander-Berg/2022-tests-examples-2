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
    'string_template',
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
    'integer_template',
    'integer',
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
    3,
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
),
(
    4,
    'integer_array_template',
    'integer',
    TRUE,
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
    code,
    conditions,
    author,
    default_locale,
    supported_locales
) VALUES
(
    'form_1',
    '{}'::JSONB,
    'nevladov',
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
    host,
    port
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
    '{{ field_1 }}',
    'form-builder.taxi.yandex.net',
    80
)
;

INSERT INTO form_builder.stages (
    id,
    form_code
) VALUES
(
    1,
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
    visibility_condition,
    external_source
) VALUES
(
    1,
    'field_1',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    ('dadata_suggests', NULL, 'data.name.short_with_opf', NULL, NULL)::form_builder.external_source_t
),
(
    1,
    'inn',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    (NULL, 'field_1', 'data.inn', FALSE, NULL)::form_builder.external_source_t
),
(
    1,
    'tax_system',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    (NULL, 'field_1', 'data.finance.tax_system', FALSE, NULL)::form_builder.external_source_t
),
(
    1,
    'registered_at',
    3,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    (NULL, 'field_1', 'data.state.registration_date', FALSE, NULL)::form_builder.external_source_t
),
(
    1,
    'field_geo_name',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    ('geo_suggests_city', NULL, 'name', NULL, NULL)::form_builder.external_source_t
),
(
    1,
    'field_geo_region',
    2,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    (NULL, 'field_geo_name', 'region_id', FALSE, NULL)::form_builder.external_source_t
),
(
    1,
    'field_dadata_bank',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    ('dadata_bank_suggests', NULL, 'data.name.payment', NULL, NULL)::form_builder.external_source_t
),
(
    1,
    'country_id_filter',
    2,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    NULL
),
(
    1,
    'country_ids_filter',
    4,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    NULL
),
(
    1,
    'country_filter',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    NULL
),
(
    1,
    'car_brand',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    ('cars_brands_suggests', NULL, 'brand', NULL, NULL)::form_builder.external_source_t
),
(
    1,
    'car_model',
    1,
    TRUE,
    FALSE,
    NULL,
    ('', 't')::form_builder.translatable,
    NULL,
    NULL,
    ('cars_models_suggests', NULL, 'model', NULL, '{"brand": "car_brand"}'::JSONB)::form_builder.external_source_t
)

;

INSERT INTO caches.geodata_regions (id, parent_id, country_id, population, region_type, last_updated_ts)
VALUES (4, NULL, NULL, 100500, 3, 100), -- белорусь
       (5, 4, 4, 10, 5, 100), -- могилёвская область
       (6, 5, 4, 5, 6, 100), -- могилёв
       (225, NULL, NULL, 100500, 3, 100),  -- россия
       (2, 225, 225, 10, 5, 100),  -- москва
       (3, 2, 225, 5, 6, 100)  -- московский
;

INSERT INTO caches.geodata_localized_names (real_name, lower_name, lang, region_id)
VALUES ('Россия', 'россия', 'ru', 225),
       ('Russia', 'russia', 'en', 225),
       ('Московская Область', 'московская область',  'ru', 2),
       ('Moscow Oblast', 'moscow oblast', 'en', 2),
       ('Москва', 'москва',  'ru', 3),
       ('Moscow', 'moscow', 'en', 3),
       ('Белорусь', 'белорусь', 'ru', 4),
       ('Могилёвская область', 'могилёвская область', 'ru', 5),
       ('Могилёв', 'могилёв', 'ru', 6)
;

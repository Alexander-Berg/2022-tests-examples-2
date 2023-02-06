INSERT INTO promotions.yql_cache (
    promotion_id,
    yandex_uid,
    user_id,
    phone_id,
    data
) VALUES
(
    'id2_yql',
    null,
    'user_id_2',
    null,
    '{"field1": "field1_data"}'::jsonb
),
(
    'id3_yql',
    null,
    'user_id_1',
    null,
    '{"val1": 10.1, "val2": "ququ"}'::jsonb
),
(
    'id1_yql',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": "field2_data"}'::jsonb
),
(
    'id1_yql',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_yql_AT',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_yql_var_l10n',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "l10n_field": 10, "plural_cnt": 2}'::jsonb
),
(
    'id_yql_var_l10n_invalid_template',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "l10n_field2": 10}'::jsonb
),
(
    'id_yql_var_l10n_no_l10n',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "l10n_field3": 10}'::jsonb
),
(
    'id_yql_var_l10n_plural',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "l10n_field": 10, "plural_0_cnt": 1, "plural_1_cnt": 2, "plural_2_cnt": 5}'::jsonb
),
(
    'id_yql_var_l10n_plural_invalid_plural',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "l10n_field": 10, "plural_cnt": "a"}'::jsonb
),
(
    'id_yql_var_l10n_no_template_for_plural',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "l10n_field": 10, "plural_cnt": 1}'::jsonb
),
(
    'id_yql_var_l10n_no_l10n_for_plural',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "l10n_field": 10, "plural_cnt": 1}'::jsonb
),
(
    'id_yql_var_locale_parametrization',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": 100500, "parametrized_field_ru": 1}'::jsonb
),
(
    'id_story_translaton_and_yql',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_story_translaton_and_yql_no_exp',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_story_translaton_and_yql_test_published',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_story_attr_text',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_story_attr_text_fail',
    null,
    'failurable_user',
    null,
    '{"field3": "field1_data", "field4": 100500}'::jsonb
),
(
    'id_deeplink_shortcuts_translaton_and_yql',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_deeplink_shortcuts_translaton_and_yql_test_published',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
),
(
    'id_deeplink_shortcuts_translaton_and_yql_no_exp',
    null,
    'user_id_1',
    null,
    '{"field1": "field1_data", "field2": 100500}'::jsonb
);

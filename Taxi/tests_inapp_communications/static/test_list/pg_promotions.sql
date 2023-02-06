INSERT INTO promotions.yql_cache (
    promotion_id,
    yandex_uid,
    user_id,
    phone_id,
    data
) VALUES
(
    'id_yql_matching_exp',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": "field2_data"}'::jsonb
),
(
    'id_yql_without_exp',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": "field2_data"}'::jsonb
),
(
    'id_yql_mismatch_exp',
    null,
    'test_user_id',
    null,
    '{"field1": "field1_data", "field2": "field2_data"}'::jsonb
);

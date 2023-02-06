INSERT INTO discounts_operation_calculations.multidraft_tasks (
    id,
    task_type,
    params,
    created_by,
    status,
    result,
    error,
    created_at,
    updated_at
) VALUES (
    'a8d1e267b27949558980b157ac8e8d73',
    'PUBLISH_SUGGEST',
    '{
        "x_yandex_login": "test_user",
        "not_approved_suggests": "",
        "suggest_id": "2",
        "active_suggest_id": 99
    }',
    'test_user',
    'COMPLETED',
    '{"multidraft_url": "test_url/multidraft/42/?multi=true"}',
    '{}',
    '2020-02-02 10:00:00',
    '2020-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d74',
    'PUBLISH_SUGGEST',
    '{
        "x_yandex_login": "test_user",
        "not_approved_suggests": "",
        "suggest_id": "3",
        "active_suggest_id": 991
    }',
    'test_user',
    'CREATED',
    '{}',
    '{}',
    '2020-02-02 10:00:00',
    '2020-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d75',
    'PUBLISH_SUGGEST',
    '{
        "x_yandex_login": "test_user",
        "not_approved_suggests": "",
        "suggest_id": "4",
        "active_suggest_id": 199
    }',
    'test_user',
    'RUNNING',
    '{}',
    '{}',
    '2020-02-02 10:00:00',
    '2020-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d76',
    'PUBLISH_SUGGEST',
    '{
        "x_yandex_login": "test_user",
        "not_approved_suggests": "",
        "suggest_id": "21",
        "active_suggest_id": 919
    }',
    'test_user',
    'FAILED',
    '{}',
    '{"message": "No discounts to create!", "code": "BadRequest::EmptyDiscountsToCreate"}',
    '2020-02-02 10:00:00',
    '2020-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d77',
    'PUBLISH_SUGGEST',
    '{"ololo": 1}',
    'test_user',
    'FAILED',
    '{}',
    '{"message": "unknown error", "code": "RuntimeError::UnknownError", "details": "detailed_info"}',
    '2020-02-02 10:00:00',
    '2020-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d83',
    'STOP_SUGGEST',
    '{
        "x_yandex_login": "test_user",
        "not_approved_suggests": "",
        "suggest_id": "5",
        "active_suggest_id": 995
    }',
    'test_user',
    'COMPLETED',
    '{"multidraft_url": "test_url/multidraft/42/?multi=true"}',
    '{}',
    '2020-02-02 10:00:00',
    '2020-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d84',
    'STOP_SUGGEST',
    '{
        "x_yandex_login": "test_user",
        "not_approved_suggests": "",
        "suggest_id": "8",
        "active_suggest_id": 998
    }',
    'test_user',
    'FAILED',
    '{}',
    '{"message": "No discounts to stop!", "code": "BadRequest::NoDiscountsToStop"}',
    '2020-02-02 10:00:00',
    '2020-02-03 10:00:00'
)
;

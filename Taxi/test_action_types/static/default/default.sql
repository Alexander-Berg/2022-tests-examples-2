INSERT INTO supportai.integrations (
    id,
    title,
    description,
    is_active,
    project_slug,
    integration_type,
    input_features,
    output_features,
    api_parameters,
    api_request
)
VALUES (
    1,
    'Выписать промокод',
    'После исполнения интеграции будет заполнена фича promocode',
    TRUE,
    'test_project',
    'change',
    '{"delivery_delay"}',
    '{"promocode"}',
    '[{"title": "Рарзмер промокода", "slug": "size" ,"type": "int", "examples": ["little", "big"]}]',
    '{
        "url": "https://test_project.ru/api/promo",
        "method": "GET",
        "body": "{ \"size\": {{size}} }",
        "timeout_s": 5,
        "retries": 5,
        "backoff_factor": 1,
        "authorization": {
            "login": "some_awesome_login",
            "password": "******",
            "encoding": "latin1"
        },
        "query_params": [
            {
                "key": "order_id",
                "value": "{{order_id}}"
            }
        ],
        "headers": [
            {
                "key": "header_1",
                "value": "value_1"
            }
        ],
        "response_mapping": [
            {
                "key": "promocode",
                "value": "$.promocode"
            }
        ]
    }'
),
(
    2,
    'не важно',
    'тоже не важно',
    TRUE,
    'test_project',
    'request',
    '{}',
    '{}',
    '[]',
    '{
        "url": "https://some-url.com",
        "method": "POST",
        "body": "<body><a>something</a><b>something else</b></body>",
        "timeout_s": 5,
        "retries": 5,
        "backoff_factor": 1,
        "query_params": [{"key": "order_id", "value": "{{order_id}}"}],
        "headers": [{"key": "header_1", "value": "value_1"}],
        "response_mapping": [{"key": "info", "value": "info"}],
        "body_format": "xml"
    }'
),
(
    3,
    'не важно',
    'тоже не важно',
    TRUE,
    'test_project',
    'request',
    '{}',
    '{}',
    '[]',
    '{
        "url": "https://some-url.com",
        "method": "POST",
        "body": "<body><a>{{something_feature}}</a><b>something else</b></body>",
        "timeout_s": 5,
        "retries": 5,
        "backoff_factor": 1,
        "query_params": [{"key": "order_id", "value": "{{order_id}}"}],
        "headers": [{"key": "header_1", "value": "value_1"}],
        "response_mapping": [{"key": "info", "value": "info"}],
        "body_format": "xml"
    }'
);

ALTER SEQUENCE supportai.integrations_id_seq RESTART WITH 4;

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
    'После исполнения интерации будет заполнена фича promocode',
    TRUE,
    'test_project',
    'request',
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
);

ALTER SEQUENCE supportai.integrations_id_seq RESTART WITH 2;

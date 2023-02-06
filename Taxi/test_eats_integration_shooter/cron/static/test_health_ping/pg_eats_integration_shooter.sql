INSERT INTO place_group_settings(
    place_group_id,
    parser_name,
    parser_options,
    integration_engine_id,
    integration_engine_options
)
VALUES
(
    'place_group_id_1',
    'retail_parser',
    '{"vendorHost": "$mockserver/eats-partner-engine-yandex-eda"}',
    NULL,
    NULL
)
;

-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO voice_gateways.voice_gateways (
    id, info.host, info.ignore_certificate,
    settings.weight, settings.disabled,
    settings.name, settings.idle_expires_in,
    token
)
VALUES
(
    'gateway_1', 'host_1', FALSE,
    10, FALSE, 'name_1', 100,
    'token_1'
 ),
(
    'gateway 2', 'host_2', TRUE,
    20, TRUE, 'name_2', 200,
    'token_2'
 );

INSERT INTO voice_gateways.disabling_history (
    id, voice_gateway_id, enabled_at, disabled_at,
    disable_reason, additional_disable_data,
    additional_enable_data, disabled_by, enabled_by,
    enable_after, relapse_count
)
VALUES
(
    1, 'gateway_1', '2020-09-22 09:10:13 +03:00', '2020-09-22 08:10:13 +03:00',
    'too many errors', NULL,
    NULL, 'GatewayChecker', NULL,
    '2020-09-22 09:10:00 +03:00', 0
),
(
    2, 'gateway_1', '2020-09-21 13:20:13 +03:00', '2020-09-21 04:10:13 +03:00',
    'too many errors', NULL,
    NULL, 'GatewayChecker', 'mazgutov',
    NULL, 1
),
(
    3, 'gateway_2', NULL, '2020-09-22 10:10:13 +03:00',
    'too many errors', NULL,
    NULL, 'GatewayChecker', NULL,
    NULL, NULL
),
(
    4, 'gateway_2', '2020-05-01 13:10:13 +03:00', '2020-04-25 10:10:13 +03:00',
    'too many errors', '{"message": "some text"}'::JSONB,
    '{"message": "they fixed errors"}'::JSONB, 'GatewayChecker', 'mazgutov',
    '2020-05-01 13:10:00 +03:00', 5
);

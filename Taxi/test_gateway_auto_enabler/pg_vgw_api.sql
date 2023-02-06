-- noinspection SqlNoDataSourceInspectionForFile

ALTER TABLE voice_gateways.voice_gateways DISABLE TRIGGER status_changed_tr;
INSERT INTO voice_gateways.voice_gateways
(
    id,
    disabled_at,
    info.host, info.ignore_certificate,
    settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
    token,
    disable_reason,
    enable_after,
    relapse_count
)
VALUES
(
    -- no records
    'gateway_id_1',
    '2021-09-11 11:00:00+03:00',
    '$mockserver', TRUE,
    10, TRUE, 'gateway_name_1', 100,
    'gateway_token_1',
    'no records',
    '2021-09-11 12:00:00+03:00',
    3
),
(
    -- no talks
    'gateway_id_2',
    '2021-09-11 11:00:00+03:00',
    '$mockserver', TRUE,
    10, TRUE, 'gateway_name_2', 100,
    'gateway_token_2',
    'no records',
    '2021-09-11 12:00:00+03:00',
    3
),
(
    -- too many errors, no relapse_count
    'gateway_id_3',
    '2021-09-11 11:00:00+03:00',
    'host_3', TRUE,
    10, TRUE, 'gateway_name_3', 100,
    'gateway_token_3',
    'too many errors',
    '2021-09-11 12:00:00+03:00',
    NULL
),
(
    -- too many errors, no enable_after
    'gateway_id_4',
    '2021-09-11 11:00:00+03:00',
    'host_4', TRUE,
    10, TRUE, 'gateway_name_4', 100,
    'gateway_token_4',
    'too many errors',
    NULL,
    1
),
(
    -- too many errors, should enable in future
    'gateway_id_5',
    '2021-09-11 11:00:00+03:00',
    'host_5', TRUE,
    10, TRUE, 'gateway_name_6', 100,
    'gateway_token_5',
    'too many errors',
    '2021-09-11 13:00:00+03:00',
    3
),
(
    -- too many errors
    'gateway_id_6',
    '2021-09-11 11:00:00+03:00',
    'host_6', TRUE,
    10, TRUE, 'gateway_name_6', 100,
    'gateway_token_6',
    'too many errors',
    '2021-09-11 12:00:00+03:00',
    3
),
(
    -- too many failed talks
    'gateway_id_7',
    '2021-09-11 11:00:00+03:00',
    'host_7', TRUE,
    10, TRUE, 'gateway_name_7', 100,
    'gateway_token_7',
    'too many failed talks',
    '2021-09-11 12:00:00+03:00',
    3
),
(
    -- too many short talks
    'gateway_id_8',
    '2021-09-11 11:00:00+03:00',
    'host_8', TRUE,
    10, TRUE, 'gateway_name_8', 100,
    'gateway_token_8',
    'too many short talks',
    '2021-09-11 12:00:00+03:00',
    3
);
ALTER TABLE voice_gateways.voice_gateways ENABLE TRIGGER status_changed_tr;

INSERT INTO forwardings.forwardings
(
    id, external_ref_id,
    gateway_id, consumer_id, state,
    created_at,
    expires_at,
    src_type, dst_type,
    caller_phone, callee_phone,
    redirection_phone, ext,
    nonce, call_location.lon, call_location.lat
)
VALUES
(
    'fwd_id_1', 'ext_ref_id_1',
    'gateway_id_1', 1, 'created',
    '2021-09-11 12:00:00+03:00',
    '2221-09-11 12:00:00+03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '999',
    'nonce1', 12.345678, 12.345678
);

INSERT INTO forwardings.talks
(
    id, created_at,
    length, forwarding_id
)
VALUES
(
    'talk_id_1',
    '2021-09-11 12:00:00+03:00',
    10, 'fwd_id_1'
),
(
    'talk_id_2',
    '2021-09-11 12:00:00+03:00',
    20, 'fwd_id_1'
),
(
    'talk_id_3',
    '2021-09-11 12:00:00+03:00',
    30, 'fwd_id_1'
);

INSERT INTO voice_gateways.disabling_history (
    voice_gateway_id, enabled_at, disabled_at,
    disable_reason, additional_disable_data,
    additional_enable_data, disabled_by, enabled_by,
    enable_after, relapse_count
)
VALUES
(
    'gateway_id_1', NULL, '2021-09-11 11:00:00+03:00',
    'no records', '{"talks": ["talk_id_1"]}'::JSONB,
    NULL, 'gateway-checker', NULL,
    '2021-09-11 12:00:00+03:00', 3
),
(
    'gateway_id_2', NULL, '2021-09-11 11:00:00+03:00',
    'no talks', NULL,
    NULL, 'gateway-checker', NULL,
    '2021-09-11 12:00:00+03:00', 3
),
(
    'gateway_id_3', NULL, '2021-09-11 11:00:00+03:00',
    'too many errors', NULL,
    NULL, 'gateway-checker', NULL,
    '2021-09-11 12:00:00+03:00', NULL
),
(
    'gateway_id_4', NULL, '2021-09-11 11:00:00+03:00',
    'too many errors', NULL,
    NULL, 'gateway-checker', NULL,
    NULL, 1
),
(
    'gateway_id_5', NULL, '2021-09-11 11:00:00+03:00',
    'too many errors', NULL,
    NULL, 'gateway-checker', NULL,
    '2021-09-11 13:00:00+03:00', 3
),
(
    'gateway_id_6', NULL, '2021-09-11 11:00:00+03:00',
    'too many errors', NULL,
    NULL, 'gateway-checker', NULL,
    '2021-09-11 12:00:00+03:00', 3
),
(
    'gateway_id_7', NULL, '2021-09-11 11:00:00+03:00',
    'too many failed talks', NULL,
    NULL, 'gateway-checker', NULL,
    '2021-09-11 12:00:00+03:00', 3
),
(
    'gateway_id_8', NULL, '2021-09-11 11:00:00+03:00',
    'too many short talks', NULL,
    NULL, 'gateway-checker', NULL,
    '2021-09-11 12:00:00+03:00', 3
);

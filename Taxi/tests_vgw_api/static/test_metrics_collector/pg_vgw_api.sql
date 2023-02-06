-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO voice_gateways.voice_gateways
(
    id, disable_reason,
    info.host, info.ignore_certificate,
    settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
    token
)
VALUES
(
    'gateway_id_1', 'too many errors',
    '$mockserver', TRUE,
    10, FALSE, 'gateway_name_1', 100,
    'gateway_token_1'
),
(
    'gateway_id_2', 'too many errors',
    '$mockserver', TRUE,
    10, TRUE, 'gateway_name_1', 100,
    'gateway_token_1'
),
(
    'gateway_id_3', NULL,
    '$mockserver', TRUE,
    10, FALSE, 'gateway_name_1', 100,
    'gateway_token_1'
);

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'consumer_name_1', TRUE),
(DEFAULT, 'consumer_name_2', FALSE);

INSERT INTO regions.regions
(id)
VALUES
(1),
(2),
(4);

INSERT INTO forwardings.forwardings
(
    id, external_ref_id,
    gateway_id, consumer_id, state,
    created_at,
    expires_at,
    src_type, dst_type,
    caller_phone, callee_phone,
    redirection_phone, ext,
    nonce, call_location.lon, call_location.lat,
    region_id
)
VALUES
(
    'fwd_id_1', 'ext_ref_id_1',
    'gateway_id_1', 1, 'created',
    '2018-02-28 19:11:13 +03:00',
    '2118-02-28 19:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '888',
    'nonce1', 12.345678, 12.345678,
    1
),
(
    'fwd_id_2', 'ext_ref_id_2',
    'gateway_id_2', 1, 'broken',
    '2018-02-28 19:11:13 +03:00',
    '2118-02-28 19:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    null, null,
    'nonce2', 12.345678, 12.345678,
    2
),
(
    'fwd_id_3', 'ext_ref_id_2',
    'gateway_id_2', 1, 'created',
    '2018-02-28 19:11:13 +03:00',
    '2118-02-28 20:11:13 +03:00',
    'passenger', 'driver',
    '+70001112233', '+79998887766',
    '+71111111111', '999',
    'nonce3', 12.345678, 12.345678,
    2
),
(
    'fwd_id_4', 'ext_ref_id_3',
    'gateway_id_2', 1, 'created',
    '2018-02-28 21:11:13 +03:00',
    '2118-02-28 22:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '777',
    'nonce001', 12.345678, 12.345678,
    NULL
),
(
    'fwd_id_5', 'ext_ref_id_3',
    'gateway_id_2', 2, 'created',
    '2018-02-28 21:11:13 +03:00',
    '2118-02-28 22:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '777',
    'nonce4', 12.345678, 12.345678,
    1
);

INSERT INTO forwardings.talks
(
    id, created_at, updated_at,
    length, forwarding_id, caller_phone,
    s3_key
)
VALUES
(
    'talk_id_1_1',
    '2018-02-28 19:12:13 +03:00',
    '2018-02-28 19:12:13 +03:00',
    10, 'fwd_id_1', '+79000000000',
    'talk_id_1_1_s3_key'
),
(
    'talk_id_1_2',
    '2018-02-28 19:11:13 +03:00',
    '2018-02-28 19:11:13 +03:00',
    20, 'fwd_id_1', '+79000000000',
    'talk_id_1_2_s3_key'
),
(
    'talk_id_1_3',
    '2018-02-28 19:16:01 +03:00',
    '2018-02-28 19:16:01 +03:00',
    30, 'fwd_id_1', '+79000000000',
    NULL
),
(
    'talk_id_1_4',
    '2018-02-28 19:17:01 +03:00',
    '2018-02-28 19:17:01 +03:00',
    40, 'fwd_id_1', '+79000000000',
    NULL
),
(  -- different client types
    'talk_id_2',
    '2018-02-28 19:11:13 +03:00',
    '2018-02-28 19:11:13 +03:00',
    20, 'fwd_id_3', '+79100000000',
    NULL
),
(  -- null region_id
    'talk_id_3',
    '2018-02-28 19:11:13 +03:00',
    '2018-02-28 19:11:13 +03:00',
    50, 'fwd_id_4', '+79100000000',
    NULL
),
(  -- old talk
    'talk_id_4',
    '2018-02-28 19:11:13 +03:00',
    '2018-02-28 18:11:13 +03:00',
    30, 'fwd_id_5', '+79100000000',
    NULL
);

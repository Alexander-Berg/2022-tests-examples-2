-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO voice_gateways.voice_gateways
(
    id,
    info.host, info.ignore_certificate,
    settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
    token
)
VALUES
(
    'gateway_id_1',
    '$mockserver', TRUE,
    10, FALSE, 'gateway_name_1', 100,
    'gateway_token_1'
),
(
    'gateway_id_2',
    '$mockserver', TRUE,
    10, TRUE, 'gateway_name_1', 100,
    'gateway_token_1'
),
(
    'gateway_id_3',
    '$mockserver', TRUE,
    10, TRUE, 'gateway_name_1', 100,
    'gateway_token_1'
);

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'consumer_name_1', TRUE),
(DEFAULT, 'consumer_name_2', FALSE);

INSERT INTO consumers.consumer_voice_gateways
(consumer_id, gateway_id)
VALUES
(1, 'gateway_id_1'),
(1, 'gateway_id_2'),
(1, 'gateway_id_3'),
(2, 'gateway_id_1');

INSERT INTO regions.regions
(id)
VALUES
(1),
(2),
(4);

INSERT INTO regions.gateway_region_settings
(
    region_id, gateway_id,
    enabled, city_id,
    enabled_for
)
VALUES
(
    1, 'gateway_id_1',
    TRUE, 'Moscow',
    '{"passenger", "driver", "dispatcher"}'
),
(
    2, 'gateway_id_1',
    TRUE, 'Saint petersburg',
    '{"driver"}'
),
(
    2, 'gateway_id_2',
    TRUE, 'Saint petersburg',
    '{"passenger", "driver"}'
),
(
    4, 'gateway_id_1',
    FALSE, 'Belgorod',
    '{"passenger", "driver"}'
);

INSERT INTO regions.vgw_enable_settings
(
    gateway_id, region_id, consumer_id,
    enabled
)
VALUES
(
    'gateway_id_1', 1, 1,
    TRUE
),
(
    'gateway_id_1', 1, 2,
    TRUE
),
(
    'gateway_id_1', 2, 1,
    TRUE
),
(
    'gateway_id_1', 2, 2,
    TRUE
),
(
    'gateway_id_2', 2, 1,
    TRUE
),
(
    'gateway_id_2', 2, 2,
    TRUE
),
(
    'gateway_id_1', 4, 1,
    FALSE
);

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
    '2018-02-26 19:11:13 +03:00',
    '2118-02-26 19:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '888',
    'nonce1', 12.345678, 12.345678
),
(
    'fwd_id_2', 'ext_ref_id_2',
    'gateway_id_2', 1, 'broken',
    '2018-02-26 19:11:13 +03:00',
    '2118-02-26 19:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    null, null,
    'nonce2', 12.345678, 12.345678
),
(
    'fwd_id_3', 'ext_ref_id_2',
    'gateway_id_2', 1, 'created',
    '2018-02-28 19:11:13 +03:00',
    '2118-02-28 20:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '999',
    'nonce3', 12.345678, 12.345678
),
(
    'fwd_id_4', 'ext_ref_id_3',
    'gateway_id_2', 1, 'created',
    '2018-02-28 21:11:13 +03:00',
    '2118-02-28 22:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '777',
    'nonce001', 12.345678, 12.345678
),
(
    'fwd_id_5', 'ext_ref_id_3',
    'gateway_id_2', 2, 'created',
    '2018-02-28 21:11:13 +03:00',
    '2118-02-28 22:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '777',
    'nonce4', 12.345678, 12.345678
);

INSERT INTO forwardings.talks
(
    id, created_at,
    length, forwarding_id, caller_phone
)
VALUES
(
    'talk_id_1',
    '2018-02-26 19:11:13 +03:00',
    10, 'fwd_id_1', '+79000000000'
),
(
    'talk_id_2',
    '2018-02-28 19:11:13 +03:00',
    20, 'fwd_id_3', '+79100000000'
),
(
    'talk_id_3',
    '2018-02-28 19:11:13 +03:00',
    30, 'fwd_id_3', '+79100000000'
);

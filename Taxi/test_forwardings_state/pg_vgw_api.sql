-- noinspection SqlNoDataSourceInspectionForFile

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
);

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'consumer_name_1', TRUE);

INSERT INTO consumers.consumer_voice_gateways
(consumer_id, gateway_id)
VALUES
(1, 'gateway_id_1');

INSERT INTO regions.regions
(id)
VALUES
(1);

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
);

INSERT INTO forwardings.forwardings
(
    id, external_ref_id,
    gateway_id, consumer_id, state, region_id,
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
    'gateway_id_1', 1, 'created', 1,
    '2022-02-24 20:11:13 +03:00',
    '2222-02-26 19:11:13 +03:00',
    'driver', 'passenger',
    '+70001110001', '+79991110001',
    '+71111111111', '111',
    'nonce1', 12.345678, 12.345678
),
(
    'fwd_id_2', 'ext_ref_id_1',
    'gateway_id_1', 1, 'created', 1,
    '2022-02-22 19:11:13 +03:00',
    '2022-02-24 20:11:13 +03:00',
    'driver', 'passenger',
    '+70002220002', '+79992220002',
    '+71111111111', '222',
    'nonce2', 12.345678, 12.345678
),
(
    'fwd_id_3', 'ext_ref_id_1',
    'gateway_id_1', 1, 'draft', 1,
    '2022-02-24 19:11:13 +03:00',
    '2222-02-26 19:11:13 +03:00',
    'driver', 'passenger',
    '+70003330003', '+79993330003',
    '+71111111111', '333',
    'nonce3', 12.345678, 12.345678
);

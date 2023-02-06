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
    10, TRUE, 'gateway_name_2', 100,
    'gateway_token_1'
);

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'consumer_name_1', TRUE);

INSERT INTO consumers.consumer_voice_gateways
(consumer_id, gateway_id)
VALUES
(1, 'gateway_id_1'),
(1, 'gateway_id_2');

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
    '{"passenger", "driver"}'
),
(
    2, 'gateway_id_1',
    TRUE, 'Saint petersburg',
    '{"driver"}'
),
(
    1, 'gateway_id_2',
    TRUE, 'Saint petersburg',
    '{"passenger", "driver"}'
),
(
    2, 'gateway_id_2',
    TRUE, 'Saint petersburg',
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
    'gateway_id_1', 2, 1,
    TRUE
),
(
    'gateway_id_2', 1, 1,
    TRUE
),
(
    'gateway_id_2', 2, 1,
    TRUE
);

INSERT INTO forwardings.forwardings
(
    id, external_ref_id, gateway_id, consumer_id, state, expires_at,
    src_type, dst_type, caller_phone, callee_phone, nonce, call_location
)
VALUES
(
    '0000000000000000000000000000000002000001', '00000000000000000000000000000000', 'gateway_id_1',
    1, 'draft', CURRENT_TIMESTAMP, 'passenger', 'driver', '+79100000000', '+79000000000', '<nonce3>',
    (37.618423, 55.751244)
);

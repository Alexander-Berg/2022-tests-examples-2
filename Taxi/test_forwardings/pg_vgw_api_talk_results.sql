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
);

INSERT INTO forwardings.talks
(
    id, created_at,
    length, forwarding_id, caller_phone,
    succeeded, status, dial_time
)
VALUES
(
    'talk_id_1',
    '2018-02-26 19:11:14 +03:00',
    10, 'fwd_id_1', '+79000000001',
    true, 'test_status_1', 10
),
(
    'talk_id_2',
    '2018-02-28 19:11:15 +03:00',
    20, 'fwd_id_1', '+79100000002',
    NULL, NULL, NULL
);

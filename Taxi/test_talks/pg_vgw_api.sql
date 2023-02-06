-- noinspection SqlNoDataSourceInspectionForFile

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
    '2018-02-26 19:11:13 +03:00',
    '2118-02-26 19:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '888',
    'nonce1', 12.345678, 12.345678,
    1
),
(
    'fwd_id_2', 'ext_ref_id_2',
    'gateway_id_2', 1, 'broken',
    '2018-02-26 19:11:13 +03:00',
    '2118-02-26 19:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    NULL, NULL,
    'nonce2', 12.345678, 12.345678,
    1
),
(
    'fwd_id_3', 'ext_ref_id_2',
    'gateway_id_2', 1, 'created',
    '2018-02-28 19:11:13 +03:00',
    '2118-02-28 20:11:13 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '999',
    'nonce3', 12.345678, 12.345678,
    NULL
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
    1
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
    id, created_at,
    length, forwarding_id, caller_phone
)
VALUES
(
    'talk_id_2',
    '2018-02-26 19:11:13 +03:00',
    10, 'fwd_id_2', '+79000000000'
);

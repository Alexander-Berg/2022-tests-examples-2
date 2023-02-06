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
    '2022-05-15 10:00:00 +03:00',
    '2022-05-15 13:00:00 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '888',
    'nonce1', 12.345678, 12.345678
),
(
    'fwd_id_2', 'ext_ref_id_2',
    'gateway_id_2', 1, 'broken',
    '2022-05-15 10:00:00 +03:00',
    '2022-05-15 13:00:00 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    null, null,
    'nonce2', 12.345678, 12.345678
),
(
    'fwd_id_3', 'ext_ref_id_2',
    'gateway_id_2', 1, 'created',
    '2022-05-12 10:00:00 +03:00',
    '2022-05-12 13:00:00 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '999',
    'nonce3', 12.345678, 12.345678
),
(
    'fwd_id_4', 'ext_ref_id_3',
    'gateway_id_2', 1, 'created',
    '2022-05-12 10:00:00 +03:00',
    '2022-05-12 13:00:00 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '777',
    'nonce001', 12.345678, 12.345678
),
(
    'fwd_id_5', 'ext_ref_id_3',
    'gateway_id_2', 2, 'created',
    '2022-05-12 10:00:00 +03:00',
    '2022-05-16 13:00:00 +03:00',
    'driver', 'passenger',
    '+70001112233', '+79998887766',
    '+71111111111', '777',
    'nonce4', 12.345678, 12.345678
);

ALTER TABLE forwardings.talks DISABLE TRIGGER forwardings_talks_set_updated_at;
INSERT INTO forwardings.talks
(
    id, created_at, updated_at,
    length, forwarding_id, caller_phone
)
VALUES
(
    'talk_id_1',
    '2022-05-15 12:00:00 +03:00',
    '2022-05-15 12:00:00 +03:00',
    10, 'fwd_id_1', '+79000000000'
),
(
    'talk_id_2',
    '2022-05-12 12:00:00 +03:00',
    '2022-05-12 12:00:00 +03:00',
    20, 'fwd_id_3', '+79100000000'
),
(
    'talk_id_3',
    '2022-05-13 12:00:00 +03:00',
    '2022-05-13 12:00:00 +03:00',
    30, 'fwd_id_3', '+79100000000'
);
ALTER TABLE forwardings.talks ENABLE TRIGGER forwardings_talks_set_updated_at;

-- noinspection SqlNoDataSourceInspectionForFile

ALTER TABLE voice_gateways.voice_gateways DISABLE TRIGGER status_changed_tr;
INSERT INTO voice_gateways.voice_gateways
(
    id,
    info.host, info.ignore_certificate,
    settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
    token, enabled_at
)
VALUES
(
    'id_1',
    '$mockserver', FALSE,
    10, FALSE, 'name_1', 100,
    'token_1', '2018-02-26 19:30:00 +03:00'
),
(
    'id_2',
    '$mockserver', TRUE,
    20, TRUE, 'name_2', 200,
    'token_2', NULL
);
ALTER TABLE voice_gateways.voice_gateways ENABLE TRIGGER status_changed_tr;

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'name_1', FALSE);

INSERT INTO regions.regions
(id)
VALUES
(1),
(2),
(3);

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
        'id_1', 1, 'created',
        '2018-02-26 19:11:13 +03:00',
        '2118-02-26 19:11:13 +03:00',
        'driver', 'passenger',
        '+70001112233', '+79998887766',
        '+71111111111', '888',
        'nonce1', 12.345678, 12.345678,
        1
    );

INSERT INTO forwardings.talks
(
    id, created_at,
    length, forwarding_id, caller_phone,
    s3_key, succeeded
)
VALUES
    (
        'talk_id_1',
        '2018-02-26 19:30:01 +03:00',
        10, 'fwd_id_1', '+79000000000',
        'talk_s3_key_1', TRUE
    ),
    (
        'talk_id_2',
        '2018-02-26 19:30:02 +03:00',
        10, 'fwd_id_1', '+79000000000',
        'talk_s3_key_2', TRUE
    ),
    (
        'talk_id_3',
        '2018-02-26 19:30:03 +03:00',
        10, 'fwd_id_1', '+79000000000',
        'talk_s3_key_3', NULL
    ),
    (
        'talk_id_4',
        '2018-02-26 19:30:04 +03:00',
        10, 'fwd_id_1', '+79000000000',
        NULL, TRUE
    ),
    (
        'talk_id_5',
        '2018-02-26 19:30:05 +03:00',
        10, 'fwd_id_1', '+79000000000',
        NULL, NULL
    ),
    (
        'talk_id_6',
        '2018-02-26 19:30:06 +03:00',
        10, 'fwd_id_1', '+79000000000',
        'talk_s3_key_6', FALSE
    ),
    (
        'talk_id_7',
        '2018-02-26 19:30:07 +03:00',
        3, 'fwd_id_1', '+79000000000',
        NULL, NULL
    ),
    (
        'talk_id_8',
        '2018-02-26 19:30:08 +03:00',
        10, 'fwd_id_1', '+79000000000',
        NULL, NULL
    ),
    (
        'talk_id_9',
        '2018-02-26 19:30:09 +03:00',
        10, 'fwd_id_1', '+79000000000',
        NULL, TRUE
    ),
    (
        'talk_id_10',
        '2018-02-26 19:30:10 +03:00',
        10, 'fwd_id_1', '+79000000000',
        NULL, TRUE
    ),
    (
        'talk_id_11',
        '2018-02-26 19:30:11 +03:00',
        10, 'fwd_id_1', '+79000000000',
        NULL, TRUE
    ),
    (
        'talk_id_12',
        '2018-02-26 19:30:12 +03:00',
        10, 'fwd_id_1', '+79000000000',
        NULL, TRUE
    );

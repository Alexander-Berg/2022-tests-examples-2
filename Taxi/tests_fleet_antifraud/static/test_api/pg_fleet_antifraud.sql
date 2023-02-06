INSERT INTO
    fleet_antifraud.operation (
        uid,
        started_at,
        created_at,
        initiator,
        name
    )
VALUES (
    999,
    '2020-01-01T00:00:00+03:00',
    '2020-01-01T00:00:00+03:00',
    'platform',
    'testsuite'
);

INSERT INTO fleet_antifraud.park_check_settings (
    uid,
    park_id,
    created_by,
    created_at,
    rule_cost_max,
    rule_duration_max,
    rule_cost_per_minute_max,
    rule_duration_min,
    rule_tips,
    rule_bonus
) VALUES (
    0,
    'PARK-01',
    999,
    '2020-01-01T00:00:00+03:00',
    1000,
    interval '1000 seconds',
    100,
    interval '100 seconds',
    100,
    NULL
), (
    2,
    'PARK-01',
    999,
    '2020-01-01T01:00:00+03:00',
    1000,
    interval '1000 seconds',
    100,
    interval '100 seconds',
    100,
    100
), (
    3,
    'PARK-02',
    999,
    '2020-01-01T01:00:00+03:00',
    1000,
    interval '1000 seconds',
    100,
    interval '100 seconds',
    100,
    100
);

INSERT INTO fleet_antifraud.park_check_latest_update (
    park_id,
    contractor_id,
    updated_at
) VALUES (
    'PARK-01',
    'CONTRACTOR-01',
    '2020-01-01T00:00:00+00:00'
);

INSERT INTO fleet_antifraud.park_check_suspicious (
    id,
    park_id,
    contractor_id,
    reason,
    reason_threshold_money,
    reason_threshold_duration,
    created_at,
    expires_at,
    order_id,
    transaction_id,
    transaction_amount,
    approved_by,
    approved_at,
    settings_id
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'PARK-01',
    'CONTRACTOR-01',
    'cost_max',
    1000,
    NULL,
    '2020-01-01T03:00:00+03:00',
    '2020-01-02T03:00:00+03:00',
    'ORDER-01',
    NULL,
    NULL,
    NULL,
    NULL,
    2
), (
    '00000000-0000-0000-0000-000000000002',
    'PARK-01',
    'CONTRACTOR-01',
    'tips',
    100,
    NULL,
    '2020-01-01T03:00:01+03:00',
    '2020-01-02T03:00:00+03:00',
    NULL,
    1,
    100,
    NULL,
    NULL,
    2
), (
    '00000000-0000-0000-0000-000000000003',
    'PARK-01',
    'CONTRACTOR-02',
    'tips',
    100,
    NULL,
    '2020-01-01T03:00:02+03:00',
    '2020-01-02T03:00:00+03:00',
    'ORDER-01',
    1,
    100,
    NULL,
    NULL,
    2
), (
    '00000000-0000-0000-0000-000000000004',
    'PARK-01',
    'CONTRACTOR-01',
    'cost_max',
    1000,
    NULL,
    '2020-01-01T03:00:03+03:00',
    '2020-01-02T03:00:00+03:00',
    'ORDER-02',
    NULL,
    NULL,
    999,
    '2020-01-01T09:00:00+03:00',
    2
), (
    '00000000-0000-0000-0000-000000000005',
    'PARK-01',
    'CONTRACTOR-01',
    'cost_max',
    1000,
    NULL,
    '2020-01-01T03:00:04+03:00',
    '2020-01-01T04:00:00+03:00',
    'ORDER-03',
    NULL,
    NULL,
    NULL,
    NULL,
    2
), (
    '00000000-0000-0000-0000-000000000006',
    'PARK-01',
    'CONTRACTOR-03',
    'duration_max',
    NULL,
    interval '1000 seconds',
    '2020-01-01T03:00:05+03:00',
    '2020-01-02T03:00:00+03:00',
    'ORDER-01',
    NULL,
    NULL,
    NULL,
    NULL,
    2
);

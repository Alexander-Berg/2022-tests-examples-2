INSERT INTO
    contractor_instant_payouts.operation (
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

INSERT INTO
    contractor_instant_payouts.rule (
        uid,
        rev,
        created_by,
        created_at,
        updated_by,
        updated_at,
        park_id,
        id,
        is_deleted,
        is_enabled,
        name,
        withdrawal_minimum,
        withdrawal_maximum,
        withdrawal_daily_maximum,
        fee_percent,
        fee_minimum,
        balance_minimum,
        is_default
    )
VALUES (
    101, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    'PARK-01', '00000000-0000-0000-0000-000000000001',
    FALSE, FALSE, 'Rule 1', 100, 100, 100, 1, 100, 100,
    FALSE
);

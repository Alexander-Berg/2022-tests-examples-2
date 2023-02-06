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
    contractor_instant_payouts.account (
        uid,
        rev,
        created_by,
        created_at,
        updated_by,
        updated_at,
        kind,
        park_id,
        id,
        is_deleted,
        is_enabled,
        name,
        modulbank_auth_token,
        modulbank_account_id,
        interpay_auth_token,
        interpay_contract_source_id,
        interpay_contract_origin_id
    )
VALUES (
    101, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    'modulbank',
    '48b7b5d81559460fb1766938f94009c1',
    '00000000-0001-0000-0000-000000000000',
    FALSE, TRUE, 'Account 1',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'a0000000-0000-0000-0000-000000000001',
    NULL, NULL, NULL
),(
    102, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    'interpay',
    '76b7b5d81559460fb1766938f94009c2',
    '00000000-0001-0000-0000-000000000000',
    FALSE, TRUE, 'Account 1',
    NULL, NULL,
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    E'\\x8fb9ca8c619d948c7248c0afff79d923b4856862a280050c99b2c6decf74662e',
    E'\\x8fb9ca8c619d948c7248c0afff79d923b4856862a280050c99b2c6decf74662e'
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
        balance_minimum
    )
VALUES (
    101, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '00000000-0000-0000-0000-000000000001',
    FALSE, TRUE, 'Rule 1',
    10, 100, 100, 0.1033, 1, 50
),(
    102, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    '76b7b5d81559460fb1766938f94009c2',
    '00000000-0000-0000-0000-000000000002',
    FALSE, TRUE, 'Rule 1',
    10, 100, 100, 0.1033, 1, 50
);

INSERT INTO
    contractor_instant_payouts.rule_target (
        uid,
        rev,
        created_by,
        created_at,
        updated_by,
        updated_at,
        park_id,
        rule_id,
        contractor_id,
        is_deleted
    )
VALUES (
    101, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '00000000-0000-0000-0000-000000000001',
    '48b7b5d81559460fb176693800000001',
    FALSE
), (
    102, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '00000000-0000-0000-0000-000000000001',
    '48b7b5d81559460fb176693800000002',
    FALSE
), (
    103, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '00000000-0000-0000-0000-000000000001',
    '48b7b5d81559460fb176693800000003',
    FALSE
), (
    104, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    '76b7b5d81559460fb1766938f94009c2',
    '00000000-0000-0000-0000-000000000002',
    '48b7b5d81559460fb176693800000001',
    FALSE
);

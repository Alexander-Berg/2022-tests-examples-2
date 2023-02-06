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
        modulbank_account_id
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
    'a0000000-0000-0000-0000-000000000001'
);

INSERT INTO
    contractor_instant_payouts.card (
        uid,
        rev,
        created_at,
        updated_at,
        park_id,
        contractor_id,
        id,
        kind,
        status,
        masked_pan,
        modulbank_auth_token,
        modulbank_card_id,
        modulbank_hashed_pan
    )
VALUES (
    101,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0001-0000-000000000000',
    'modulbank',
    'active',
    '************1234',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'c0000000-0000-0000-0000-000000000001',
    E'\\x'
), (
    102,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000002',
    '00000000-0001-0002-0000-000000000000',
    'modulbank',
    'active',
    '************5678',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'c0000000-0000-0000-0000-000000000002',
    E'\\x'
), (
    103,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000003',
    '00000000-0001-0003-0000-000000000000',
    'modulbank',
    'active',
    '************5678',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'c0000000-0000-0000-0000-000000000003',
    E'\\x'
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
    10, 100, 100, 0.1, 1, 50
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
);

INSERT INTO
    contractor_instant_payouts.contractor_payout (
        id,
        park_id,
        contractor_id,
        account_id,
        card_id,
        created_at,
        updated_at,
        withdrawal_amount,
        debit_amount,
        debit_fee,
        transfer_amount,
        progress_status,
        transfer_status
    )
VALUES (
    '00000000-0001-0002-0001-000000000000',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000002',
    '00000000-0001-0000-0000-000000000000',
    '00000000-0001-0002-0000-000000000000',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    0,
    0,
    0,
    0,
    'transfer',
    '{}'
), (
    '00000000-0001-0003-0001-000000000000',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000003',
    '00000000-0001-0000-0000-000000000000',
    '00000000-0001-0003-0000-000000000000',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T13:00:00+03:00',
    90.01,
    90.01,
    9.001,
    90.01,
    'succeeded',
    '{}'
);

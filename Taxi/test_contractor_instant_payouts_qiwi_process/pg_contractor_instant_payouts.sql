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
        park_id,
        id,
        kind,
        is_deleted,
        is_enabled,
        name,
        qiwi_agent_id,
        qiwi_point_id,
        qiwi_bearer_token
    )
VALUES (
    101,
    0,
    999,
    '2020-01-01T12:00:00+03:00',
    999,
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '00000000-0001-0000-0000-000000000000',
    'qiwi',
    FALSE,
    FALSE,
    'Account 1',
    E'\\x8fb9ca8c619d948c7248c0afff79d923b4856862a280050c99b2c6decf74662e',
    E'\\xd0526c18b4db3b736c900c57754e7c7895df4656802f894d78542266961297e3',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5'
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
        qiwi_card_token
    )
VALUES (
    101,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0001-0000-000000000000',
    'qiwi',
    'active',
    '************1234',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5'
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
    '00000000-0001-0001-0001-000000000000',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0000-0000-000000000000',
    '00000000-0001-0001-0000-000000000000',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T13:00:00+03:00',
    '100.0000',
    '100.0000',
    '1.0101',
    '100.0000',
    'transfer',
    '{}'
);

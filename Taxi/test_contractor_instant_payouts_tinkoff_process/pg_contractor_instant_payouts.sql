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
        tinkoff_terminal,
        tinkoff_password
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
    'tinkoff',
    FALSE,
    FALSE,
    'Account 1',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
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
        tinkoff_terminal,
        tinkoff_card_id
    )
VALUES (
    101,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0001-0000-000000000000',
    'tinkoff',
    'active',
    '************1234',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5'
);

INSERT INTO
    contractor_instant_payouts.contractor_payout (
        id,
        park_id,
        contractor_id,
        account_id,
        method,
        card_id,
        bank_id,
        phone_pd_id,
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
    'card',
    '00000000-0001-0001-0000-000000000000',
    NULL,
    NULL,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T13:00:00+03:00',
    '100.0101',
    '100.0101',
    '1.0101',
    '100.0101',
    'transfer',
    '{}'
), (
    '00000000-0001-0001-0001-000000000001',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0000-0000-000000000000',
    'sbp',
    NULL,
    'bank1',
    'pd_id1',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T13:00:00+03:00',
    '100.0101',
    '100.0101',
    '1.0101',
    '100.0101',
    'transfer',
    '{}'
), (
    '00000000-0001-0001-0001-100000000000',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0000-0000-000000000000',
    'card',
    '00000000-0001-0001-0000-000000000000',
    NULL,
    NULL,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T13:00:00+03:00',
    '100.0101',
    '100.0101',
    '1.0101',
    '100.0101',
    'transfer',
    '{
        "bpid": "2353039"
    }'
), (
    '00000000-0001-0001-0001-100000000001',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0000-0000-000000000000',
    'sbp',
    NULL,
    'bank1',
    'pd_id1',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T13:00:00+03:00',
    '100.0101',
    '100.0101',
    '1.0101',
    '100.0101',
    'transfer',
    '{
        "bpid": "2353039"
    }'
);

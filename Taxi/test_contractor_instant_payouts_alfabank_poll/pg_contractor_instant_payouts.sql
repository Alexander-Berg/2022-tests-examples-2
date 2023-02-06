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
        mozen_park_token
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
    'alfabank',
    FALSE,
    FALSE,
    'Account 1',
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
        mozen_park_token,
        mozen_card_id
    )
VALUES (
    101,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0001-0000-000000000000',
    'alfabank',
    'active',
    '************1234',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'c0000000-0000-0000-0000-000000000001'
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
    '{
        "bpid": "00000001-0002-0003-0004-000000000005",
        "bpst": "in_progress",
        "repc": 0
     }'
), (
    '00000000-0001-0001-0001-000000000001',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0000-0000-000000000000',
    'sbp',
    NULL,
    'bank_id1',
    'pb_id1',
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T13:00:00+03:00',
    '100.0101',
    '100.0101',
    '1.0101',
    '100.0101',
    'transfer',
    '{
        "bpid": "00000001-0002-0003-0004-000000000005",
        "bpst": "in_progress",
        "repc": 0
     }'
);

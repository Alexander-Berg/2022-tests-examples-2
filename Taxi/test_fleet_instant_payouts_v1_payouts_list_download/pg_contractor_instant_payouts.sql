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
        mozen_park_token
    )
VALUES (
    101, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    'modulbank',
    'park1',
    '00000000-0001-0000-0000-000000000000',
    FALSE, FALSE, 'Account 1',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'a0000000-0000-0000-0000-000000000001',
    NULL
), (
    102, 0,
    999, '2020-01-01T12:00:00+03:00',
    999, '2020-01-01T12:00:00+03:00',
    'alfabank',
    'park1',
    '00000000-0002-0000-0000-000000000000',
    FALSE, FALSE, 'Account 2',
    NULL,
    NULL,
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
        modulbank_auth_token,
        modulbank_card_id,
        modulbank_hashed_pan,
        mozen_park_token,
        mozen_card_id
    )
VALUES (
    101,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'park1',
    'contractor1',
    '00000000-0001-0001-0000-000000000000',
    'modulbank',
    'active',
    '************1234',
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'c0000000-0000-0000-0000-000000000001',
    E'\\x',
    NULL,
    NULL
), (
    102,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    'park1',
    'contractor1',
    '00000000-0002-0002-0000-000000000000',
    'alfabank',
    'active',
    '************5678',
    NULL,
    NULL,
    NULL,
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'c0000000-0000-0000-0000-000000000001'
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
        transfer_fee,
        progress_status,
        error_code,
        transfer_status
    )
VALUES (
    '00000000-0001-0001-0001-000000000000',
    'park1',
    'contractor1',
    '00000000-0001-0000-0000-000000000000',
    '00000000-0001-0001-0000-000000000000',
    '2020-01-01T12:00:00+00:00',
    '2020-01-01T13:00:00+00:00',
    '100.0101',
    '100.0101',
    '1.0101',
    '100.0101',
    '0.0101',
    'succeeded',
    NULL,
    '{"bpid": "3c178bd1-f720-4daf-99b8-b8ab253f3810", "bpst": "completed", "repc": 0}'
), (
    '00000000-0001-0001-0002-000000000000',
    'park1',
    'contractor1',
    '00000000-0001-0000-0000-000000000000',
    '00000000-0001-0001-0000-000000000000',
    '2020-02-02T12:00:00+00:00',
    '2020-02-02T13:00:00+00:00',
    '200.0202',
    '200.0202',
    '2.0202',
    '200.0202',
    NULL,
    'failed',
    'account_insufficient_funds',
    '{"bpid": "3c178bd1-f720-4daf-99b8-b8ab253f3811", "bpst": "failed", "repc": 0}'
), (
    '00000000-0001-0001-0003-000000000000',
    'park1',
    'contractor1',
    '00000000-0002-0000-0000-000000000000',
    '00000000-0002-0002-0000-000000000000',
    '2020-03-03T12:00:00+00:00',
    '2020-03-03T13:00:00+00:00',
    '300.0101',
    '300.0101',
    '3.0101',
    '300.0101',
    '0.0101',
    'succeeded',
    NULL,
    '{"bpid": "3c178bd1-f720-4daf-99b8-b8ab253f3812", "bpst": "completed", "repc": 0}'
);

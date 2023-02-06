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
        is_notification_enabled,
        notification_balance_threshold,
        notification_recipient_user_ids,
        modulbank_auth_token,
        modulbank_account_id
    )
VALUES (
    101,
    0,
    999,
    '2020-01-01T12:00:00+03:00',
    999,
    '2020-01-01T12:00:00+03:00',
    'PARK-01',
    '00000000-0000-0000-0000-000000000001',
    'modulbank',
    FALSE,
    TRUE,
    'Account 1',
    TRUE,
    500.0500,
    DEFAULT,
    E'\\xFB50422FC2854AEF447403734F28022A2F0E90C6AD8BBE12F9A5665D2F0054EBB7B9C676EFB2704270ED179291C3EBD5',
    'a0000000-0000-0000-0000-000000000001'
), (
    102,
    0,
    999,
    '2020-01-01T13:00:00+03:00',
    999,
    '2020-01-01T13:00:00+03:00',
    'PARK-02',
    '00000000-0000-0000-0000-000000000002',
    'modulbank',
    FALSE,
    TRUE,
    'Account 2',
    TRUE,
    2000.0500,
    ARRAY['user1', 'user2']::TEXT[],
    E'\\xD01FDC1C9801136D8A30DC1E5985CAE5677482333344DD0188F95FB6EAC4BDA28080ED76551A53B6999EB0C8DB556D7B',
    'a0000000-0000-0000-0000-000000000001'
), (
    103,
    0,
    999,
    '2020-01-01T14:00:00+03:00',
    999,
    '2020-01-01T14:00:00+03:00',
    'PARK-03',
    '00000000-0000-0000-0000-000000000003',
    'modulbank',
    FALSE,
    TRUE,
    'Account 3',
    FALSE,
    DEFAULT,
    DEFAULT,
    E'\\x1D3C2626C6F0404DDE1FFAD6F9DF5D81F1C2FB43FD0D50FD87DAF105FBB8E568A4CBE18BA1FAB6D5BD978B54C00CDE47',
    'a0000000-0000-0000-0000-000000000001'
), (
    104,
    0,
    999,
    '2020-01-01T15:00:00+03:00',
    999,
    '2020-01-01T15:00:00+03:00',
    'PARK-01',
    '00000000-0000-0000-0000-100000000001',
    'modulbank',
    TRUE,
    FALSE,
    'Account 2',
    DEFAULT,
    DEFAULT,
    DEFAULT,
    E'\\x4E99E809EEF1142A4A0E3823B6FDAE63EFC8C579438B3B344A153B4A35F781F7B264FEBE5A178E17C4FB32DD3BF23387',
    'a0000000-0000-0000-0000-000000000001'
);

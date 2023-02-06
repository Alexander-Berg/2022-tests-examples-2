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
        interpay_auth_token,
        interpay_contract_source_id,
        interpay_contract_origin_id
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
    'interpay',
    FALSE,
    FALSE,
    'Account 1',
    E'\\x5a9040f6cdc9a7cea9ee0dfa8698023e76f85bd940295e696f64654e6f006d04',
    E'\\xa97e57e2e0f42f9267d51ac0c8ceba285802ce8fe4f0265428f7b51a67e38c67',
    E'\\x'
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
        interpay_card_token
    )
VALUES (
    101,
    0,
    '2020-01-01T12:00:00+03:00',
    '2020-01-01T12:00:00+03:00',
    '48b7b5d81559460fb1766938f94009c1',
    '48b7b5d81559460fb176693800000001',
    '00000000-0001-0001-0000-000000000000',
    'interpay',
    'active',
    '************1234',
    E'\\x2e822bf0995a8ec66a81be496fd1289ae0c1a978326d11e969c2d2f96de01704'
);

INSERT INTO
    contractor_instant_payouts.contractor_payout (
        id,
        park_id,
        contractor_id,
        account_id,
        card_id,
        method,
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
    '00000000-0001-0001-0000-000000000000',
    'card',
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
);

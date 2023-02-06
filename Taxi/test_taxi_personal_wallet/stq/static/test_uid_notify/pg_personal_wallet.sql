insert into personal_wallet.wallets
    (id, yandex_uid, currency, updated_at, created_at, merged_at, merge_status)
    VALUES
    -- portal_uid and phonish_uid are bound
    -- portal wallets
    ('wallet_id/1', 'portal_uid', 'RUB', NOW(), NOW(), null, null),  -- #1
    ('wallet_id/4', 'portal_uid', 'EUR', NOW(), NOW(), null, null),  -- #4
    -- phonish wallets
    ('wallet_id/5', 'phonish_uid', 'RUB', NOW(), NOW(), null, null),-- should be merged with #1
    ('wallet_id/6', 'phonish_uid', 'EUR', NOW(), NOW(), null, null),-- should be merged with #4
    ('wallet_id/7', 'phonish_uid', 'UAH', NOW(), NOW(), null, null),-- should be merged with a newly created wallet

    -- not bounded wallets
    ('wallet_id/other_uid', 'other_uid', 'RUB', NOW(), NOW(), null, null), -- should not be merged
    ('wallet_id/8', 'phonish_uid_already_merged', 'RUB', NOW(), NOW(), '2020-05-27 17:05:42.221206', 'merged')

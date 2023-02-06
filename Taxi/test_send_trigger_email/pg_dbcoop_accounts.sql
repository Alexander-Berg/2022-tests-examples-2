
INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, has_specific_limit, currency_code, email_id) VALUES
    ('account1', null, 'family', 'FFFFFF', '+0300', 1, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', 'no_payment_method', True, 'rub', 'account1_email'),
    ('account2', null, 'family', 'FFFFFF', '+0300', 1, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', 'no_payment_method', True, 'rub', null);

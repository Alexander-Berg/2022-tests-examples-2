
INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, has_specific_limit, currency_code, email_id, passport_family_id) VALUES
    ('acc1', null, 'family', 'FFFFFF', '+0300', 1, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', 'no_payment_method', True, 'rub', 'account1_email', NULL),
    ('acc2', null, 'family', 'FFFFFF', '+0300', 1, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', 'no_payment_method', True, 'rub', 'account1_email', 'f124');

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, limit_amount, revision) VALUES
    ('memb1', 'acc1', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision0'),
    ('memb2', 'acc1', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa02', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision0'),
    ('memb3', 'acc1', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa03', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision0');

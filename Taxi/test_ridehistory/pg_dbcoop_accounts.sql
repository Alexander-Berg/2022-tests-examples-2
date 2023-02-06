INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, error_description, revision, currency_code, email_id, report_frequency, next_report_date, has_specific_limit, limit_amount) VALUES
    ('1', null, 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', 'RUB', null, null, null, FALSE, null),
    ('2', 'Ивановы Inc.', 'business', 'FFFFFF', '+0300', 0, 'user2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', 'RUB', null, null, null, FALSE, null);

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, limit_amount, revision) VALUES
    ('memb1', '1', 'Petrov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision2');

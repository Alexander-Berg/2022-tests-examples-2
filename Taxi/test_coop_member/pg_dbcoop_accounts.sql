INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, has_specific_limit, limit_amount) VALUES
    ('acc1', 'Петровы', 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc2', 'Артемий', 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc3', null, 'family', 'FFFFFF', '+0300', 0, 'user2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc4', null, 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc5', 'Фродо-фродер', 'business', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc6', 'Леголас', 'business', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc7', 'Саруман', 'business', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc8', 'Бильбо', 'business', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc9', 'Гендальф', 'business', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc_business', 'Бизнес', 'business', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('acc403', 'Чужой акк', 'family', 'FFFFFF', '+0300', 0, 'user2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision0', false, null),
    ('18', 'С лимитом', 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', true, 50000000);

INSERT INTO coop_accounts.attempt_counters (account_id, week_start_reference, attempt_count) VALUES
    ('acc5', NOW(), 25),
    ('acc7', NOW() - INTERVAL '7 days 1 hour', 30),
    ('acc9', NOW() - INTERVAL '6 days 23 hour', 30),
    ('acc8', NOW(), 24);

-- Passport_family

INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, currency_code, has_specific_limit, passport_family_id) VALUES
    ('acc_with_passport_family', null, 'family', 'FFFFFF', '+0300', 1, 'user_with_passport_family', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, null, True, 'f124');

INSERT INTO coop_accounts.phonish_family_members_invite (id, account_owner_yandex_uid, account_owner_phone_id, member_id, member_phone_id, account_id) VALUES
    ('5920bf6750ed4baaa7f997646d7b4bdb', 'user_with_passport_family', 'owner_phone_id', 'member_id', '00aaaaaaaaaaaaaaaaaaaa10', 'acc_with_passport_family');

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, limit_amount, revision) VALUES
    ('memb1', 'acc1', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision0'),
    ('memb2', 'acc1', 'Sidorov Jr.', '00aaaaaaaaaaaaaaaaaaaa02', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision3'),
    ('memb3', 'acc1', 'Sidorov Deleted', '00aaaaaaaaaaaaaaaaaaaa03', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), False, True, True, True, null, 'revision4'),
    ('memb4', 'acc1', 'Sidorov Not Accepted', '00aaaaaaaaaaaaaaaaaaaa04', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, False, True, null, 'revision4'),
    ('memb11', 'acc2', 'Artemy Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision2'),
    ('memb12', 'acc2', 'Artemy Jr.', '00aaaaaaaaaaaaaaaaaaaa02', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision3'),
    ('memb13', 'acc2', 'Artemy JrJr', '00aaaaaaaaaaaaaaaaaaaa03', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision4'),
    ('memb14', 'acc2', 'Artemy Not Accepted', '00aaaaaaaaaaaaaaaaaaaa04', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision4'),
    ('memb21', 'acc3', 'Others User', '00aaaaaaaaaaaaaaaaaaaa01', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision4'),
    ('memb211', 'acc3', 'Others Owner', '00aaaaaaaaaaaaaaaaaaaa03', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision4'),
    ('memb22', 'acc4', 'Others User', '00aaaaaaaaaaaaaaaaaaaa01', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision4'),
    ('memb403', 'acc403', 'Nor Sidorov nor Artemy', '00aaaaaaaaaaaaaaaaaaaa05', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, False, True, null, 'revision5'),
    ('memb30', '18', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision0'),
    ('memb31', '18', 'Пользователь с лимитом', '00aaaaaaaaaaaaaaaaaaaa05', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 50000000, 'revision11'),
    ('memb100', 'acc_with_passport_family', 'Ivanov Sr.', '00aaaaaaaaaaaaaaaaaaaa10', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision0'),
    ('memb101', 'acc_with_passport_family', 'Ivanov Jr.', '00aaaaaaaaaaaaaaaaaaaa11', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, null, 'revision3');


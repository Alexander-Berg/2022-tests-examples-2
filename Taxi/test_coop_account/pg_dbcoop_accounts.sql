INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, error_description, revision, currency_code, email_id, report_frequency, next_report_date, has_specific_limit, limit_amount) VALUES
    ('1', null, 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', 'RUB', null, null, null, FALSE, null),
    ('2', 'Ивановы Inc.', 'business', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', null, 'id-corp@inc.com', 'never', null, FALSE, null),
    ('3', 'Ивановы Inc.', 'business', 'FFFFFF', '+0300', 0, 'user2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', 'RUB', null, null, null, FALSE, null),
    ('403', 'Ивановы Inc.', 'family', 'FFFFFF', '+0300', 0, 'user_other', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', 'USD', null, null, null, FALSE, null),
    ('13', 'Не активный', 'family', 'FFFFFF', '+0300', 0, 'user_other_2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), False, 'some_reason', 'revision1', null, null, null, null, FALSE, null),
    ('14', 'Удаленный', 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, null, 'revision1', null, null, null, null, FALSE, null),
    ('15', 'Удаленный', 'family', 'FFFFFF', '+0300', 0, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), False, null, 'revision1', null, null, null, null, FALSE, null),
    ('16', 'Без карты', 'family', 'FFFFFF', '+0300', 0, 'user2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, 'no_payment_method', 'revision1', null, null, null, null, FALSE, null),
    ('17', 'Деактивированный', 'family', 'FFFFFF', '+0300', 0, 'user2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, 'payment_failed', 'revision1', null, null, null, null, FALSE, null),
    ('18', 'С лимитом', 'family', 'FFFFFF', '+0300', 0, 'user3', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', null, null, null, null, TRUE, 50000000),
    ('19', null, 'family', 'FFFFFF', '+0300', 0, 'user4', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision5', null, null, null, null, FALSE, null),
    ('7', 'Ивановы Inc. 7', 'business', 'FFFFFF', '+0300', 0, 'user7', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', 'RUB', null, null, null, FALSE, null);

-- Test plus-multy subs
INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, error_description, revision, currency_code, email_id, report_frequency, next_report_date, has_specific_limit, limit_amount, passport_family_id) VALUES
    ('100', null, 'family', 'FFFFFF', '+0300', 0, 'user_with_family', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, null, 'revision1', 'RUB', null, null, null, FALSE, null, 'f1234');

INSERT INTO coop_accounts.shared_payments (id, type, payment_method_id, account_id, is_main, persistent_id, deleted_at) VALUES
    ('sp1', 'card', 'pm_id', '1', True, 'label1', null),
    ('sp3', 'card', 'pm_unbound', '1', False, 'label1', null),
    ('sp4', 'card', 'pm_id2', '2', True, 'label1', null),
    ('sp5', 'card', 'pm_id2', '13', False, 'label1', null),
    ('sp6', 'card', 'pm_id6', '18', True, 'label1', null),
    ('sp7', 'card', 'pm_id6', '16', True, 'label1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP)),
    ('sp8', 'card', 'pm_id7', '100', True, 'label7', null);

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, limit_amount, revision) VALUES
    ('memb1', '1', 'Petrov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision2'),
    ('memb2', '1', 'Petrov Jr.', '00aaaaaaaaaaaaaaaaaaaa02', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision3'),
    ('memb3', '1', 'Petrov Deleted', '00aaaaaaaaaaaaaaaaaaaa03', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, True, True, False, null, 'revision4'),
    ('memb4', '1', 'Petrov Not Accepted', '00aaaaaaaaaaaaaaaaaaaa04', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, False, False, null, 'revision4'),
    ('memb5', '1', 'Petrov Inactive', '00aaaaaaaaaaaaaaaaaaaa05', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, True, True, False, null, 'revision5'),
    ('memb6', '13', 'Petrov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision2'),
    ('memb11', '2', 'Иванов', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision11'),
    ('memb12', '18', 'Владелец аккаунта с лимитом', '00aaaaaaaaaaaaaaaaaaaa03', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision11'),
    ('memb13', '18', 'Пользователь с лимитом', '00aaaaaaaaaaaaaaaaaaaa04', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 50000000, 'revision11'),
    ('memb14', '17', 'Пользователь с лимитом', '00aaaaaaaaaaaaaaaaaaaa04', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 12340000, 'revision11'),
    ('memb20', '7', 'Ivanov Sr.', 'phone_id1', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision1'),
    ('memb100', '100', 'Petrov Sr.', '00aaaaaaaaaaaaaaaaaaaa10', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision2');

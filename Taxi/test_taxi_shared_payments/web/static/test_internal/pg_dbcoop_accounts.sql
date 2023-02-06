INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, currency_code, has_specific_limit) VALUES
    ('acc1', null, 'family', 'FFFFFF', '+0300', 1, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, null, True),
    ('acc3', 'С просроченной картой', 'business', 'fff000', '+0300', 2, 'user2', CAST('2018-02-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision2', null, null, False),
    ('acc4', 'С отвязанной картой', 'business', 'fff000', '+0300', 2, 'user2', CAST('2018-02-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision2', null, null, False),
    ('acc5', 'Удаленный', 'business', 'fff000', '+0300', 2, 'user1', CAST('2018-02-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, 'revision2', null, null, False),
    ('acc6', 'Портальный', 'business', 'fff000', '+0300', 2, 'portal_user1', CAST('2019-02-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision2', null, null, False),
    ('acc7', 'Без привязанных карт', 'business', 'fff000', '+0300', 2, 'user7', CAST('2018-02-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, null, False),
    ('acc403', 'ООО "Ромашка"', 'family', '000FFF', '-0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-02-02 10:00:00.000001' AS TIMESTAMP), True, 'revision3', null, null, True),
    ('acc_limits', 'ООО "Ромашка"', 'family', '000FFF', '-0300', 3, 'user3', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision3', null, null, True);

-- Test has_rides:
INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, currency_code, has_specific_limit, has_rides) VALUES
    ('acc2', 'Ивановы Inc.', 'business', 'fff000', '+0300', 2, 'user1', CAST('2018-02-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, 'revision2', 'no_payment_method', 'EUR', False, True),
    ('acc_wo_name', null, 'business', 'fff000', '+0300', 1, 'user777', CAST('2018-02-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, 'revision2', 'no_payment_method', 'EUR', False, True),
    ('acc_with_rides', null, 'family', 'FFFFFF', '+0300', 1, 'user_for_rides', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, null, True, True),
    ('acc_without_rides', null, 'family', 'FFFFFF', '+0300', 1, 'user_for_rides', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, null, True, False),
    ('acc_deleted', null, 'family', 'FFFFFF', '+0300', 1, 'user_for_rides', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, 'revision1', null, null, True, True);

-- Test passport_family
INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, currency_code, has_specific_limit, passport_family_id) VALUES
    ('acc_with_passport_family', null, 'family', 'FFFFFF', '+0300', 1, 'user_with_passport_family', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, null, True, 'f124'),
    ('acc_with_passport_family_without_card', null, 'family', 'FFFFFF', '+0300', 1, 'user_with_passport_family_no_card', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, null, True, 'f124');


UPDATE coop_accounts.accounts SET limit_amount=1000000 where id='acc_limits';

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, limit_amount, revision) VALUES
    ('memb1', 'acc1', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 5000000, 'revision2'),
    ('memb2', 'acc1', 'Sidorov Jr.', '00aaaaaaaaaaaaaaaaaaaa02', 'user', CAST('2018-01-03 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision3'),
    ('memb3', 'acc1', 'Sidorov Deleted', '00aaaaaaaaaaaaaaaaaaaa03', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, True, True, False, null, 'revision4'),
    ('memb4', 'acc1', 'Sidorov Not Accepted', '00aaaaaaaaaaaaaaaaaaaa04', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, False, False, null, 'revision4'),
    ('memb403', 'acc403', 'Not Sidorov', '00aaaaaaaaaaaaaaaaaaaa05', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, False, False, null, 'revision5'),
    ('memb_lim', 'acc_limits', 'Not Sidorov', '00aaaaaaaaaaaaaaaaaaaa07', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, False, True, 5000000, 'revision5'),
    ('memb5', 'acc2', 'A user', '00aaaaaaaaaaaaaaaaaaaa01', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision4'),
    ('memb6', 'acc3', 'A user', 'phone_expired', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision4'),
    ('memb7', 'acc4', 'A user', 'phone_unbound', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision4'),
    ('memb8', 'acc6', 'A user', '00aaaaaaaaaaaaaaaaaaaa06', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision4'),
    ('memb9', 'acc6', 'A user', '00aaaaaaaaaaaaaaaaaaaa01', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, False, null, 'revision4'),
    ('memb10', 'acc7', 'A user', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 5000000, 'revision1'),
    ('memb11', 'acc_with_passport_family', 'A user', '00aaaaaaaaaaaaaaaaaaaa10', 'owner', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision4'),
    ('memb12', 'acc_with_passport_family_without_card', 'A user', '00aaaaaaaaaaaaaaaaaaaa11', 'owner', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision4'),
    ('memb13', 'acc_with_passport_family', 'A user', '00aaaaaaaaaaaaaaaaaaaa12', 'user', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision4');

INSERT INTO coop_accounts.shared_payments (id, type, payment_method_id, account_id, is_main, persistent_id, deleted_at) VALUES
    ('sp1', 'card', 'pm_1', 'acc1', True, 'label1', null),
    ('sp12', 'card', 'pm_1', 'acc6', True, 'label1', null),
    ('sp2', 'card', 'pm_expired', 'acc3', True, 'label1', null),
    ('sp3', 'card', 'pm_unbound', 'acc4', True, 'label1', null),
    ('sp4_0', 'card', 'pm_1', 'acc2', True, 'label1', null),
    ('sp4_1', 'card', 'pm_deleted_0', 'acc2', True, 'label1', CAST('2018-01-03 10:00:00.000001' AS TIMESTAMP)),
    ('sp5_0', 'card', 'pm_deleted_1', 'acc_limits', True, 'label1', CAST('2018-01-03 10:00:00.000001' AS TIMESTAMP)),
    ('sp5_1', 'card', 'pm_deleted_2', 'acc_limits', True, 'label1', CAST('2018-01-02 10:00:00.000001' AS TIMESTAMP)),
    ('sp6', 'card', 'pm_2', 'acc_with_passport_family', True, 'label1', null);

INSERT INTO coop_accounts.stats (account_id, member_id, spent, month) VALUES
    ('acc1', 'memb1', 2000000, CAST('2019-06-01 00:00:00.0' AS TIMESTAMPTZ)),
    ('acc1', 'memb2', 2000000, CAST('2019-06-01 00:00:00.0' AS TIMESTAMPTZ)),
    ('acc_limits', 'memb_lim', 2000000, CAST('2019-06-01 00:00:00.0-03:00' AS TIMESTAMPTZ)),
    ('acc2', 'memb5', 300000, CAST('2019-12-01 00:00:00.000000+03:00' AS TIMESTAMP));

INSERT INTO coop_accounts.transactions (id, order_id, event, member_id, amount, created_at) VALUES
    ('tr_1', 'order_id_1', 'hold', 'memb1', 1000000, now()),
    ('tr_2', 'order_id_1', 'hold', 'memb1', 1000000, now());

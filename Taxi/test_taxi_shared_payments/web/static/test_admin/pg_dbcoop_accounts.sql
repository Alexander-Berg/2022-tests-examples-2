INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, currency_code, has_specific_limit) VALUES
    ('acc1', 'SomeFamily', 'family', 'FFFFFF', '+0300', 1, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), '2021-02-20T17:09:19Z', null, False, 'revision1', null, null, False);

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, limit_amount, revision) VALUES
    ('memb1', 'acc1', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 5000000, 'revision2'),
    ('memb2', 'acc1', 'Sidorov Jr.', '00aaaaaaaaaaaaaaaaaaaa02', 'user', CAST('2018-01-03 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 1000000, 'revision3');

INSERT INTO coop_accounts.shared_payments (id, type, payment_method_id, account_id, is_main, persistent_id, deleted_at) VALUES
    ('sp1', 'card', 'pm_1', 'acc1', True, 'label1', null),
    ('sp2', 'card', 'pm_2', 'acc1', False, 'label2', null);                                                                                                                           ;

INSERT INTO coop_accounts.debt_orders (order_id, account_id, created_at) VALUES
    ('order_a', 'acc1', CAST('2019-01-04 10:00:00.000001' AS TIMESTAMP)),
    ('order_b', 'acc3', CAST('2019-01-04 10:00:00.000001' AS TIMESTAMP));

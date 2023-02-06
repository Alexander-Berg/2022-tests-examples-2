INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, error_description, has_specific_limit, currency_code) VALUES
    ('acc1', null, 'family', 'FFFFFF', '+0300', 1, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', 'no_payment_method', True, 'rub');

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, revision) VALUES
    ('memb1', 'acc1', 'Sidorov Sr.', '00aaaaaaaaaaaaaaaaaaaa01', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 'revision2');

INSERT INTO coop_accounts.shared_payments (id, type, payment_method_id, account_id, is_main, persistent_id) VALUES
    ('sp1', 'card', 'pm_1', 'acc1', True, 'label1');

INSERT INTO coop_accounts.stats (account_id, member_id, spent, month) VALUES
    ('acc1','memb1', 200, CAST('2019-06-01 00:00:00.0' AS TIMESTAMPTZ));

INSERT INTO coop_accounts.transactions (id, order_id, event, member_id, amount, created_at) VALUES
    ('tr_1', 'order_id_1', 'hold', 'memb1', 100, now()),
    ('tr_2', 'order_id_1', 'hold', 'memb1', 100, now());

INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision) VALUES
    ('1', null, 'family', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, 'revision1'),
    ('2', null, 'family', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1'),
    ('3', null, 'family', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), False, 'revision1'),
    ('4', null, 'family', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, 'revision1'),
    ('5', 'Ивановы Inc. 1', 'business', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, 'revision1'),
    ('6', 'Ивановы Inc. 2', 'business', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), False, 'revision1'),
    ('7', 'Ивановы Inc. 3', 'business', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1'),
    ('8', 'Ивановы Inc. 4', 'business', 'FFFFFF', '+0300', 3, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, 'revision1');

-- INSERT INTO coop_accounts.shared_payments (id, type, payment_method_id, account_id, is_main, persistent_id) VALUES
--     ('sp1', 'card', 'pm_id', '1', True, 'label1'),
--     ('sp2', 'card', 'pm_id2', '1', False, 'label1'),
--     ('sp3', 'card', 'pm_unbound', '1', False, 'label1'),
--     ('sp4', 'card', 'pm_id2', '2', False, 'label1'),
--     ('sp5', 'card', 'pm_id2', '3', False, 'label1');

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, revision) VALUES
    ('memb1', '1', 'Petrov Sr.', 'phone_id1', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 'revision2'),
    ('memb2', '1', 'Petrov Jr.', 'phone_id2', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 'revision3'),
    ('memb3', '1', 'Petrov Deleted', 'phone_id3', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), True, True, True, True, 'revision4'),
    ('memb4', '1', 'Petrov Not Accepted', 'phone_id4', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, False, True, 'revision4'),
    ('memb5', '1', 'Petrov Inactive', 'phone_id5', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, False, True, True, True, 'revision5');

INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision, email_id, report_frequency, next_report_date) VALUES
    ('7', 'Ивановы Inc. 7', 'business', 'FFFFFF', '+0300', 2, 'user1', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', 'engineer@yandex-team.ru', '2 4 * * wed', CAST('2019-09-11 10:00:00.000001' AS TIMESTAMP) ),
    ('2', 'Ивановы Inc. 2', 'business', 'FFFFFF', '+0300', 0, 'user2', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1', null, '2 4 * * wed', CAST('2019-09-11 10:00:00.000001' AS TIMESTAMP) )
;

INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, revision) VALUES
    ('memb1', '7', 'Ivanov Sr.', 'phone_id1', 'owner', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 'revision1'),
    ('memb2', '7', 'Ivanov Jr.', 'phone_id2', 'user', CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP), null, True, True, True, True, 'revision2')
;

INSERT INTO coop_accounts.accounts (id, name, type, color, tz_offset, members_number, owner_id, created_at, updated_at, deleted_at, is_active, revision) VALUES
    ('A1', null, 'family', 'FFFFFF', '+0300', 5, 'M0', CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), null, True, 'revision1');


INSERT INTO coop_accounts.phonish_family_members_invite (id, account_owner_yandex_uid, account_owner_phone_id, member_id, member_phone_id, account_id, created_at, is_already_portal) VALUES
    ('I1', 'OWNER_UID', 'P0', 'M1', 'P1', 'A1', CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), False),
    ('I2', 'OWNER_UID', 'P0', 'M2', 'P2', 'A1', CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), False ),
    ('I3', 'OWNER_UID', 'P0', 'M3', 'P3', 'A1', CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), False),
    ('I4', 'OWNER_UID', 'P0', 'M4', 'P4', 'A1', CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), True);


INSERT INTO coop_accounts.members (id, account_id, nickname, phone_id, role, created_at, updated_at, deleted_at, is_active, is_invitation_sent, is_invitation_accepted, has_specific_limit, revision) VALUES
    ('M0', 'A1', '_', 'P0', 'owner', CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), null,                                           True, True, True,  True, 'revision2'),
    ('M1', 'A1', '_', 'P1', 'user' , CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), null,                                           True, True, True,  True, 'revision3'),
    ('M2', 'A1', '_', 'P2', 'user' , CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP),True, True, True,  True, 'revision4'),
    ('M3', 'A1', '_', 'P3', 'user' , CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), null,                                           True, True, False, True, 'revision4'),
    ('M4', 'A1', '_', 'P4', 'user' , CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2021-01-01 10:00:00.000001' AS TIMESTAMP), null,                                           True, True, False, True, 'revision4');


-- Test plus-multy subs
INSERT INTO db_family.invite (id, family_id, family_owner_uid, invite_id, member_phone_id, image, text, created_at, updated_at, status) VALUES
('invalid_invite', 'f1', '2', 'invalid_invite', '00aaaaaaaaaaaaaaaaaaaa01', 'image', 'text', '2021-01-01 00:00:00.000000', '2021-01-01 00:00:00.000000', 'new'),
('valid_invite', 'f1', '2', 'valid_invite', '00aaaaaaaaaaaaaaaaaaaa02', 'image1', 'text1', '2021-01-01 00:00:00.000000', '2021-01-01 00:00:00.000000', 'new'),
('valid_invite_2', 'f2', '4', 'valid_invite_2', '00aaaaaaaaaaaaaaaaaaaa02', 'image2', 'text2', '2021-01-01 00:00:00.000000', '2021-01-01 00:00:00.000000', 'new');

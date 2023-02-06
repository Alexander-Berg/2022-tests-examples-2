ALTER SEQUENCE alias_sequence RESTART WITH 3000000;

INSERT INTO eats_tips_partners.alias (alias, type, migrated)
VALUES
('3000000', 'partner', true),
('3000010', 'partner', true),
('3000020', 'partner', true)
;



INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id, phone_id, deleted_at, status)
VALUES
('00000000-0000-0000-0000-000003000000', '3000000', '3000000', '3000000', 'ok_id_0', NULL, NULL ),
('00000000-0000-0000-0000-000003000010', '3000010', '3000010', '3000010', 'ok_id_1', NULL, 'registered'),
('00000000-0000-0000-0000-000003000020', '3000020', '3000020', '3000020', 'ok_id_2', NULL, 'new' )
;

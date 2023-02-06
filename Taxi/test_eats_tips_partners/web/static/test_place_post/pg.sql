ALTER SEQUENCE alias_sequence RESTART WITH 3000000;

INSERT INTO eats_tips_partners.role (slug, title)
VALUES
('recipient', 'recipient'),
('admin', 'admin'),
('unknown', 'unknown role')
;


INSERT INTO eats_tips_partners.alias (alias, type)
VALUES
('0000100', NULL),
('0000120', 'place_partner')
;

INSERT INTO eats_tips_partners.alias (alias, type, migrated)
VALUES
('0000110', 'partner', true),
('0000130', 'partner', true),
('0000140', 'place', true),
('0000150', 'partner', true)
;


INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id, phone_id, deleted_at)
VALUES
('00000000-0000-0000-0000-000000000010', '0000100', '10', '10', 'ok_phone_id', NULL),
('00000000-0000-0000-0000-000000000011', '0000110', '11', '11', 'deleted_partner', NOW()),
('00000000-0000-0000-0000-000000000013', '0000130', '13', '13', 'phone_id_13', NULL),
('00000000-0000-0000-0000-000000000015', '0000150', '15', '15', NULL, NULL)
;

INSERT INTO eats_tips_partners.place (id, alias, owner)
VALUES
('00000000-0000-0000-0000-000000000014', '0000140', '00000000-0000-0000-0000-000000000013')
;

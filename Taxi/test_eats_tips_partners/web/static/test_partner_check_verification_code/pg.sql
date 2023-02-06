ALTER SEQUENCE alias_sequence RESTART WITH 3000000;

INSERT INTO eats_tips_partners.role (slug, title)
VALUES
('recipient', 'recipient'),
('admin', 'admin'),
('unknown', 'unknown role')
;

INSERT INTO eats_tips_partners.alias (alias, type, deleted_at, migrated)
VALUES
('0000100', 'partner', NOW(), true),
('3000010', 'partner', NULL, true)
;


INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id, phone_id, deleted_at, status)
VALUES
('00000000-0000-0000-0000-000000000010', '0000100', '10', '10', 'phone_id_10', NOW(), NULL),
('00000000-0000-0000-0000-000003000010', '3000010', '3000010', '3000010', 'phone_id_13', NULL, 'registered')
;

ALTER SEQUENCE alias_sequence RESTART WITH 3000000;

INSERT INTO eats_tips_partners.alias (alias, type)
VALUES
('0000010', NULL), ('0000030', NULL), ('0000100', NULL), ('0000110', 'place_partner')
;


INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id)
VALUES
('00000000-0000-0000-0000-000000000001', NULL, '1', '1'),
('00000000-0000-0000-0000-000000000003', NULL, '3', '3'),
('00000000-0000-0000-0000-000000000010', NULL, '10', '10'),
('00000000-0000-0000-0000-000000000011', '0000110', '11', '11')
;


INSERT INTO eats_tips_partners.place (id, alias, mysql_id)
VALUES
('10000000-0000-0000-0000-000000000003', '0000030', '3'),
('10000000-0000-0000-0000-000000000010', '0000100', '10')
;


INSERT INTO eats_tips_partners.places_partners (place_id, partner_id, alias, confirmed, show_in_menu, deleted_at, roles)
VALUES
('10000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', '0000030', true, false, NULL, '{admin}'),
('10000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000010', '0000100', true, false, NULL, '{admin}'),
('10000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000011', '0000110', true, false, NULL, '{recipient}')
;

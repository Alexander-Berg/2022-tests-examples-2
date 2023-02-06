ALTER SEQUENCE alias_sequence RESTART WITH 3000000;

INSERT INTO eats_tips_partners.alias (alias)
VALUES
('0000030'), ('0000180'), ('0000190')
;

INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id)
VALUES
('00000000-0000-0000-0000-000000000003', NULL, '3', '3'),
('00000000-0000-0000-0000-000000000018', '0000180', '18', '18'),
('00000000-0000-0000-0000-000000000019', '0000190', '19', '19')
;


INSERT INTO eats_tips_partners.place (id, alias, mysql_id)
VALUES
('10000000-0000-0000-0000-000000000003', '0000030', '3')
;


INSERT INTO eats_tips_partners.places_partners (place_id, partner_id, alias, confirmed, show_in_menu, roles, not_migrated)
VALUES
('10000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', '0000030', true, false, '{admin}', true)
;

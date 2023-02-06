ALTER SEQUENCE alias_sequence RESTART WITH 3000000;

INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id)
VALUES
('00000000-0000-0000-0000-000000000010', null, '10', '10'),
('00000000-0000-0000-0000-000000000011', null, '11', '11')
;


INSERT INTO eats_tips_partners.place (id, alias, mysql_id, deleted_at)
VALUES
('10000000-0000-0000-0000-000000000109', null, '109', null)
;


INSERT INTO eats_tips_partners.place_invitation (place_id, phone_id, status, partner_id, role, created_at)
VALUES
('10000000-0000-0000-0000-000000000109', 'phone_id_10', 'invited', NULL, 'recipient', '2021-09-16T18:53:04+03:00'),
('10000000-0000-0000-0000-000000000109', 'phone_id_10', 'invited', NULL, 'admin', '2021-09-16T18:53:04+03:00'),
('10000000-0000-0000-0000-000000000109', 'phone_id_10', 'declined_by_place', NULL, 'admin', '2021-09-16T18:53:04+03:00'),
('10000000-0000-0000-0000-000000000109', 'awesome_phone_id', 'invited', NULL, 'recipient', '2021-09-16T18:53:04+03:00')
;

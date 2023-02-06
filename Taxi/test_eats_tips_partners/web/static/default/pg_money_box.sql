INSERT INTO eats_tips_partners.alias (alias, type)
VALUES
('0000010', 'partner'),
('0000020', 'partner'),
('0000030', 'partner'),
('0000040', 'partner'),
('0001000', 'place'),
('0001010', 'place'),
('0001020', 'place'),
('0002000', 'money_box'),
('0002010', 'money_box'),
('0002020', 'money_box')
;

INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id, deleted_at)
VALUES
('00000000-0000-0000-0000-000000000001', '0000010', '1', '1', null),
('00000000-0000-0000-0000-000000000002', '0000020', '2', '2', null),
('00000000-0000-0000-0000-000000000003', '0000030', '3', '3', null),
('00000000-0000-0000-0000-000000000004', '0000040', '4', '4', null)
;

INSERT INTO eats_tips_partners.brand (id, slug)
VALUES
('99999999-0000-0000-0000-000000000001', 'shoko')
;

INSERT INTO eats_tips_partners.place (id, alias, mysql_id, deleted_at, brand_id)
VALUES
('10000000-0000-0000-0000-000000000100', '0001000', '100', null, '99999999-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000101', '0001010', '101', null, null),
('10000000-0000-0000-0000-000000000102', '0001020', '102', null, null)
;

INSERT INTO eats_tips_partners.places_partners (place_id, partner_id, roles, confirmed, show_in_menu, deleted_at)
VALUES
('10000000-0000-0000-0000-000000000100', '00000000-0000-0000-0000-000000000001', '{admin}', true, false, null),
('10000000-0000-0000-0000-000000000100', '00000000-0000-0000-0000-000000000002', '{recipient}', true, true, null),
('10000000-0000-0000-0000-000000000100', '00000000-0000-0000-0000-000000000003', '{recipient}', false, true, null),
('10000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000001', '{admin}', true, false, null),
('10000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000004', '{recipient}', true, false, null)
;

INSERT INTO eats_tips_partners.money_box (
  id,
  place_id,
  fallback_partner_id,
  display_name,
  alias,
  created_at,
  deleted_at
)
VALUES
('20000000-0000-0000-0000-000000000200', '10000000-0000-0000-0000-000000000100', '00000000-0000-0000-0000-000000000001', 'копилка 1', '0002000', '2021-10-30 14:00:00+00', null),
('20000000-0000-0000-0000-000000000201', '10000000-0000-0000-0000-000000000100', '00000000-0000-0000-0000-000000000001', 'копилка 2', '0002010', '2021-10-30 14:00:00+00', null),
('20000000-0000-0000-0000-000000000202', '10000000-0000-0000-0000-000000000100', '00000000-0000-0000-0000-000000000001', 'копилка 3', '0002020', '2021-10-30 14:00:00+00', '2021-10-30 15:00:00+00')
;
INSERT INTO eats_tips_partners.role (slug, title)
VALUES
('recipient', 'recipient'),
('admin', 'admin'),
('unknown', 'unknown role')
;


INSERT INTO eats_tips_partners.alias (alias, type)
VALUES
('0000100', 'partner'),
('0001000', 'place')
;


INSERT INTO eats_tips_partners.partner (id, alias, b2p_id, mysql_id, phone_id)
VALUES
('00000000-0000-0000-0000-000000000010', '0000100', '10', '10', 'existing_phone_id')
;


INSERT INTO eats_tips_partners.place (id, alias, mysql_id)
VALUES
('10000000-0000-0000-0000-000000000100', '0001000', '100')
;

INSERT INTO eats_tips_partners.sms_history (
    phone_id,
    status,
    status_text,
    status_code,
    sms_id,
    created_at,
    intent
)
VALUES
('already_sent_sms_phone_id', 'OK', 'OK', '100', '220-220', '2022-01-01T11:50:00+00:00', 'eats_tips_invite_partner'),
('ok_phone_id', 'OK', 'OK', '100', '220-219', '2021-12-30T12:00:00+00:00', 'eats_tips_invite_partner')
;


INSERT INTO eats_tips_partners.place_invitation (
    place_id,
    phone_id,
    partner_id,
    role,
    status,
    created_at
)
VALUES
('10000000-0000-0000-0000-000000000100', 'ok_phone_id', NULL, 'admin', 'invited', NOW()),
('10000000-0000-0000-0000-000000000100', 'existing_phone_id', NULL, 'admin', 'invited', NOW()),
('10000000-0000-0000-0000-000000000100', 'already_sent_sms_phone_id', NULL, 'admin', 'invited', NOW()),
('10000000-0000-0000-0000-000000000100', 'bad_format_phone_id', NULL, 'admin', 'invited', NOW())
;

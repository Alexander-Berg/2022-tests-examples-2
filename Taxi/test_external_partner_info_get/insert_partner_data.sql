INSERT INTO eats_partners.roles (slug, title, id, created_at, updated_at, deleted_at)
VALUES ('ROLE_ADMIN', 'admin', 1, '2020-07-19 11:00:00', '2020-07-19 11:00:00', null),
       ('ROLE_LOL', 'lol', 2, '2020-07-19 11:00:00', '2020-07-19 11:00:00', null),
       ('ROLE_ASD', 'asd', 3, '2020-07-19 11:00:00', '2020-07-19 11:00:00', null);


INSERT INTO eats_partners.partners (partner_id, personal_email_id, timezone, country_code, is_fast_food,
                                    is_blocked, blocked_at, first_login_at, created_at, updated_at, partner_uuid)
VALUES (1, 'partner1@partner.com_id', 'Europe/Moscow', 'RU', false, false, null,
        '2019-07-19 11:12:39.933000', '2020-07-19 08:12:47.377382', '2021-07-19 08:12:47.377382', '1b9d70ef-d667-4c9c-9b20-c61209ea6332'),
       (2, 'partner2@partner.com_id', 'Europe/Moscow', 'KZ', true, true, '2021-05-05 11:00:00',
        '2019-07-19 11:12:39.933000', '2020-07-19 08:12:47.377382', '2021-07-19 08:12:47.377382', '1b9d70ef-d667-4c9c-9b20-c61209ea6333');

INSERT INTO eats_partners.partner_places (partner_id, place_id, created_at)
VALUES (1, 123, '2020-07-19 08:15:23.433401'),
       (1, 234, '2020-07-19 08:15:23.433401'),
       (1, 343, '2020-07-19 08:15:23.433401'),
       (2, 111, '2020-07-19 08:32:10.038861'),
       (2, 222, '2020-07-19 08:32:10.038861');

INSERT INTO eats_partners.partner_roles (partner_id, role_id, created_at)
VALUES (1, 1, '2020-07-19 11:13:16.425000'),
       (1, 2, '2020-07-19 11:13:30.537000'),
       (2, 1, '2020-07-19 08:31:01.919519'),
       (2, 3, '2020-07-19 08:31:01.919519');

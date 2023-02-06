INSERT INTO eats_partners.roles (slug, title, id, created_at, updated_at, deleted_at)
VALUES ('ROLE_ADMIN', 'admin', 1, '2020-07-19 11:00:00', '2020-07-19 11:00:00', null),
       ('ROLE_LOL', 'lol', 2, '2020-07-19 11:00:00', '2020-07-19 11:00:00', null),
       ('ROLE_OPERATOR', 'asd', 3, '2020-07-19 11:00:00', '2020-07-19 11:00:00', null);

INSERT INTO eats_partners.partners (partner_id, personal_email_id, timezone, country_code, is_fast_food,
                                    is_blocked, blocked_at, first_login_at, created_at, updated_at, partner_uuid)
VALUES (69, 'test@test.test_id', 'Europe/Moscow', 'KZ', true, true, '2021-05-05 11:00:00',
        '2019-07-19 11:12:39.933000', '2020-07-19 08:12:47.377382', '2021-07-19 08:12:47.377382', '1b9d70ef-d667-4c9c-9b20-c61209ea6332');

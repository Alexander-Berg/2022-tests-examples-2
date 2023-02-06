INSERT INTO eats_partners.partners (partner_id, personal_email_id, timezone, country_code, is_fast_food,
                                    is_blocked, blocked_at, first_login_at, created_at, updated_at, partner_uuid)
VALUES (1, 'partner1@partner.com_id', 'Europe/Moscow', 'RU', false, false, null,
        '2019-07-19 11:12:39.933000', '2020-07-19 08:12:47.377382', '2021-07-19 08:12:47.377382', '1b9d70ef-d667-4c9c-9b20-c61209ea6332'),
       (2, 'partner2@partner.com_id', 'Europe/Moscow', 'KZ', true, true, '2021-05-05 11:00:00',
        '2019-07-19 11:12:39.933000', '2020-07-19 08:12:47.377382', '2021-07-19 08:12:47.377382', '1b9d70ef-d667-4c9c-9b20-c61209ea6333');

INSERT INTO eats_partners.action_tokens (partner_id, token, created_at, updated_at)
VALUES
       (1, '123456789', '2020-01-01 01:00:00.000000', '2020-01-01 01:00:00.000000+00'),
       (2, '123456789', '2020-01-01 01:00:00.000000', '2020-12-01 01:00:00.000000+00');

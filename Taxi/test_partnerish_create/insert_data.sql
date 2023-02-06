INSERT INTO eats_partners.partners (partner_id, personal_email_id, timezone, country_code, is_fast_food,
                                    is_blocked, blocked_at, first_login_at, created_at, updated_at, partner_uuid)
VALUES (1, 'partner1@partner.com_id', 'Europe/Moscow', 'RU', false, false, null,
        '2019-07-19 11:12:39.933000', '2020-07-19 08:12:47.377382', '2021-07-19 08:12:47.377382', '1b9d70ef-d667-4c9c-9b20-c61209ea6332'),
       (2, 'partner2@partner.com_id', 'Europe/Moscow', 'KZ', true, true, '2021-05-05 11:00:00',
        '2019-07-19 11:12:39.933000', '2020-07-19 08:12:47.377382', '2021-07-19 08:12:47.377382', '1b9d70ef-d667-4c9c-9b20-c61209ea6333');

INSERT INTO eats_partners.partnerish (uuid, email, name, rest_name, city, address, phone_number, consent_to_data_processing, personal_email_id, country_code, is_accepted, partner_id)
VALUES
('abcd1', 'email1@test.ya', 'Test', 'Vkusno', 'SPb', 'Goroh street 491', '+79997778500', true, NULL, 'RU', false, NULL ),
('abcd2', 'email2@test.ya', 'Test', 'Vkusno', 'SPb', 'Goroh street 492', '+79997778500', true, NULL, 'RU', true, 492492 ),
('abcd3', 'email3@test.ya', 'Test', 'Vkusno', 'SPb', 'Goroh street 493', '+79997778500', true, NULL, NULL, false, NULL ),
('abcd4', 'email4@test.ya', 'Test', 'Vkusno', 'SPb', 'Goroh street 494', '+79997778500', true, 'personal_email4_id', 'RU', false, NULL );

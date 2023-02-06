INSERT INTO eats_place_subscriptions.subscriptions (place_id,
                                                    tariff,
                                                    is_partner_updated,
                                                    is_trial,
                                                    valid_until,
                                                    activated_at,
                                                    created_at,
                                                    updated_at)
VALUES (123, 'business', false, false, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00'),
       (124, 'business_plus', false, false, now(), now(), now(), now()),
       (125, 'free', false, false,  '2020-05-01T03:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+00:00'),
       (126, 'free', false, false, now(), now(), now(), now()),
       (127, 'business', false, false, now(), now(), now(), now()),
       (128, 'business_plus', true, true, now(), now(), now(), now()),
       (129, 'business_plus', false, false, now(), now(), now(), now()),
       (130, 'business_plus', false, false, now(), now(), now(), now());

INSERT INTO eats_place_subscriptions.places (place_id,
                                             business_type,
                                             country_code,
                                             timezone,
                                             region_id,
                                             created_at)
VALUES (123, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (124, 'store', 'ru', 'Asia/Yekaterinburg', 1, now()),
       (125, 'restaurant', 'ru', 'America/Sao_Paulo', 1, now()),
       (126, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       --- 127 not found ---
       (128, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (129, 'restaurant', 'ru', 'Europe/Moscow', 1, now());

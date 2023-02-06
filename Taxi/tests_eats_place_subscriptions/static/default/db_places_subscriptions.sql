INSERT INTO eats_place_subscriptions.subscriptions (place_id,
                                                    tariff,
                                                    next_tariff,
                                                    is_partner_updated,
                                                    is_trial,
                                                    valid_until,
                                                    activated_at,
                                                    created_at,
                                                    updated_at,
                                                    last_partner_downdate_time)
VALUES (123, 'business', NULL, false, false, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00',
        '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', NULL),
       (124, 'business_plus', NULL, true, false, now(), now(), now(), now(), NULL),
       (125, 'free', NULL, true, false, '2020-05-01T03:00:00+00:00', '2020-04-28T12:00:00+00:00',
        '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+00:00', NULL),
       (126, 'free', NULL, false, false, '2020-07-30T21:00:00+00:00', '2020-07-30T21:00:00+00:00', now(), now(), NULL),
       (127, 'business', NULL, false, false, '2020-07-30T21:00:00+00:00', '2020-07-30T21:00:00+00:00', now(), now(), NULL),
       (128, 'business_plus', NULL, true, true, '2020-07-30T21:00:00+00:00', '2020-07-30T21:00:00+00:00', now(), now(), NULL),
       (130, 'free', NULL, false, false, '2020-07-30T21:00:00+00:00', '2020-07-30T21:00:00+00:00', now(), now(), NULL),
       (131, 'free', NULL, false, false, '2020-07-30T21:00:00+00:00', '2020-07-30T21:00:00+00:00', now(), now(), NULL),
       (132, 'free', NULL, false, false, '2020-07-30T21:00:00+00:00', '2020-07-30T21:00:00+00:00', now(), now(), NULL),
       (133, 'business_plus', 'business', false, false, '2020-04-30T19:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', NULL),
       (134, 'business_plus', 'free', false, false, '2020-04-30T19:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', '2020-04-29T19:00:00+00:00'),
       (135, 'business_plus', NULL, false, false, '2020-04-30T19:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', '2020-04-30T19:00:00+00:00'),
       (136, 'business', NULL, false, false, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', NULL),
       (137, 'business', NULL, false, false, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', '2020-04-29T21:00:00+00:00'),
       (138, 'business', NULL, false, false, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', '2020-04-30T21:00:00+00:00'),
       (139, 'free', NULL, false, false, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00', '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00', NULL);

INSERT INTO eats_place_subscriptions.subscriptions (place_id,
                                                    tariff,
                                                    next_tariff,
                                                    is_partner_updated,
                                                    is_trial,
                                                    next_is_trial,
                                                    valid_until,
                                                    activated_at,
                                                    created_at,
                                                    updated_at)
VALUES (129, 'business', 'business_plus', true, true, true, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00', now(), now());

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
       (129, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       --- 130 not found ---
       (131, 'restaurant', 'by', 'Europe/Moscow', 134, now()),
       (132, 'restaurant', 'kz', 'Asia/Almaty', 125, now()),
       (133, 'restaurant', 'ru', 'Asia/Yekaterinburg', 1, now()),
       (134, 'restaurant', 'ru', 'Asia/Yekaterinburg', 1, now()),
       (135, 'restaurant', 'ru', 'Asia/Yekaterinburg', 1, now()),
       (136, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (137, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (139, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (138, 'restaurant', 'ru', 'Europe/Moscow', 1, now());

INSERT INTO eats_place_subscriptions.subscription_order_counter
(
 place_id,
 date,
 count
)
VALUES
      (123, '2020-04-10'::date, 10),
      (123, '2020-04-15'::date, 5),
      (123, '2020-04-20'::date, 5),
      (123, '2020-04-25'::date, 11);

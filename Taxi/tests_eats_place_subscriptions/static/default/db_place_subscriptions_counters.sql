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
VALUES (111, 'business', null, false, false, false, '2020-01-30T21:00:00+00:00', '2020-01-28T12:00:00+00:00',
        '2020-01-28T12:00:00+03:00', '2020-01-28T12:00:00+03:00'),
       (222, 'business', null, false, false, false, '2020-02-28T21:00:00+00:00', '2020-02-25T12:00:00+00:00',
        '2020-02-25T12:00:00+03:00', '2020-02-25T12:00:00+03:00'),
       (333, 'business_plus', null, false, false, false, '2020-03-30T21:00:00+00:00', '2020-03-28T12:00:00+00:00',
        '2020-03-28T12:00:00+03:00', '2020-03-28T12:00:00+03:00'),
       (444, 'business_plus', null, false, true, true, '2020-04-30T21:00:00+00:00', '2020-04-28T12:00:00+00:00',
        '2020-04-28T12:00:00+03:00', '2020-04-28T12:00:00+03:00'),
       (555, 'business', 'business', false, false, false, '2020-05-30T21:00:00+00:00', '2020-05-28T12:00:00+00:00',
        '2020-05-28T12:00:00+03:00', '2020-05-28T12:00:00+03:00'),
       (666, 'business', 'business', false, false, false, '2020-06-30T21:00:00+00:00', '2020-06-28T12:00:00+00:00',
        '2020-06-28T12:00:00+03:00', '2020-06-28T12:00:00+03:00'),
       (777, 'business_plus', 'business_plus', false, false, false, '2020-07-30T21:00:00+00:00',
        '2020-07-28T12:00:00+00:00',
        '2020-07-28T12:00:00+03:00', '2020-07-28T12:00:00+03:00'),
       (888, 'business_plus', 'business_plus', false, false, false, '2020-08-30T21:00:00+00:00',
        '2020-08-28T12:00:00+00:00', '2020-08-28T12:00:00+03:00', '2020-08-28T12:00:00+03:00'),
       (999, 'business', null, false, false, false, '2020-09-30T21:00:00+00:00',
        '2020-08-28T12:00:00+00:00', '2020-08-28T12:00:00+03:00', '2020-08-28T12:00:00+03:00'),
       (1111, 'business_plus', null, false, false, false, '2020-10-30T21:00:00+00:00',
        '2020-08-28T12:00:00+00:00', '2020-08-28T12:00:00+03:00', '2020-08-28T12:00:00+03:00'),
       (2222, 'business_plus', 'business', false, false, false, '2020-11-30T21:00:00+00:00',
        '2020-08-28T12:00:00+00:00', '2020-08-28T12:00:00+03:00', '2020-08-28T12:00:00+03:00'),
       (3333, 'business_plus', 'business_plus', false, false, false, '2020-12-30T21:00:00+00:00',
        '2020-08-28T12:00:00+00:00', '2020-08-28T12:00:00+03:00', '2020-08-28T12:00:00+03:00');
;

INSERT INTO eats_place_subscriptions.places (place_id,
                                             business_type,
                                             country_code,
                                             timezone,
                                             region_id,
                                             created_at)
VALUES (111, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (222, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (333, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (444, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (555, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (666, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (777, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (888, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (999, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (1111, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (2222, 'restaurant', 'ru', 'Europe/Moscow', 1, now()),
       (3333, 'restaurant', 'ru', 'Europe/Moscow', 1, now());

-- no trial - 31 order - borders [2020-01-01 - 2020-01-30]
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (111, '2020-01-01'::date, 10),
       (111, '2020-01-15'::date, 5),
       (111, '2020-01-20'::date, 5),
       (111, '2020-01-30'::date, 11);

-- trial - 29 order - borders [2020-01-30 - 2020-02-28]
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (222, '2020-01-30'::date, 10),
       (222, '2020-02-15'::date, 5),
       (222, '2020-02-20'::date, 5),
       (222, '2020-02-28'::date, 9);

-- no trial - 31 order - business_plus - borders [2020-03-01 - 2020-03-30]
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (333, '2020-03-01'::date, 10),
       (333, '2020-03-15'::date, 5),
       (333, '2020-03-20'::date, 5),
       (333, '2020-03-30'::date, 11);

-- no trial - 29 order - business_plus - borders [2020-03-31 - 2020-04-30]
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (444, '2020-03-31'::date, 10),
       (444, '2020-04-15'::date, 5),
       (444, '2020-04-20'::date, 5),
       (444, '2020-04-30'::date, 9);

-- no trial - 31 order - borders [2020-05-01 - 2020-05-30]
-- next not null
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (555, '2020-05-01'::date, 10),
       (555, '2020-05-15'::date, 5),
       (555, '2020-05-20'::date, 5),
       (555, '2020-05-30'::date, 11);

-- trial - 29 order - borders [2020-06-01 - 2020-06-30]
-- next not null
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (666, '2020-06-01'::date, 10),
       (666, '2020-06-15'::date, 5),
       (666, '2020-06-20'::date, 5),
       (666, '2020-06-30'::date, 9);

-- no trial - 31 order - business_plus - borders [2020-07-01 - 2020-07-30]
-- next not null
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (777, '2020-07-01'::date, 10),
       (777, '2020-07-15'::date, 5),
       (777, '2020-07-20'::date, 5),
       (777, '2020-07-30'::date, 11);

-- no trial - 29 order - business_plus - borders [2020-08-01 - 2020-08-30]
-- next not null
INSERT INTO eats_place_subscriptions.subscription_order_counter
(place_id,
 date,
 count)
VALUES (888, '2020-08-01'::date, 10),
       (888, '2020-08-15'::date, 5),
       (888, '2020-08-20'::date, 5),
       (888, '2020-08-30'::date, 9);

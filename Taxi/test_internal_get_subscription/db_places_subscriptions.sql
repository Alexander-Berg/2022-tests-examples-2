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
VALUES (201, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz - interval '1 days', '2020-04-28T12:00:00+00:00', now(), now()),
       (202, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, '2020-04-28T12:00:00+00:00', now(), now()),
       (203, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz + interval '1 days', '2020-04-28T12:00:00+00:00', now(), now()),
       (204, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz + interval '2 days', '2020-04-28T12:00:00+00:00', now(), now()),
       (205, 'business', NULL, false, true, false, '2020-02-06T05:59:00+03:00'::timestamptz, '2020-04-28T12:00:00+00:00', now(), now()),
       (206, 'business', NULL, false, true, false, '2020-02-06T06:00:01+03:00'::timestamptz, '2020-04-28T12:00:00+00:00', now(), now()),                     -- more then 3 days + delta_time

       (207, 'business', NULL, false, false, false, '2020-02-02T15:00:00+03:00'::timestamptz, '2020-04-28T12:00:00+00:00', now(), now()),                    -- is _trial false
       (208, 'business', 'free', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, '2020-04-28T12:00:00+00:00', now(), now()),                   -- next_tariff free
       (209, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, '2020-04-28T12:00:00+00:00', now(), now()),
       (210, 'business', NULL, false, true, true, '2020-02-06T05:59:00+03:00'::timestamptz, '2020-04-28T12:00:00+00:00', now(), now());                      -- next_is_trial false

INSERT INTO eats_place_subscriptions.places (place_id,
                                             business_type,
                                             country_code,
                                             timezone,
                                             region_id,
                                             created_at,
                                             inn)

VALUES (201, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (202, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (203, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (204, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (205, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (206, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),

       (207, 'restaurant', 'ru', 'UTC', 1, now(), '222222'),
       (208, 'restaurant', 'ru', 'UTC', 1, now(), '222222'),
       (209, 'restaurant', 'ru', 'UTC', 1, now(), NULL);

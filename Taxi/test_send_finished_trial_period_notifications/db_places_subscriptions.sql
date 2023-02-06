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
VALUES (201, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz - interval '1 days', now(), now(), now()),
       (202, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),
       (203, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz + interval '1 days', now(), now(), now()),
       (204, 'business', NULL, false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz + interval '2 days', now(), now(), now()),
       (205, 'business', NULL, false, true, false, '2020-02-06T05:59:00+03:00'::timestamptz, now(), now(), now()),
       (206, 'business', NULL, false, true, false, '2020-02-06T06:00:01+03:00'::timestamptz, now(), now(), now()),                     -- more then 3 days + delta_time

       (207, 'business', NULL, false, false, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),                    -- is _trial false
       (208, 'business', 'free', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),                   -- next_tariff free
       (209, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),          -- inn null
       (210, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),
       (220, 'business', 'business_plus', false, true, true, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),          -- next_is_trial true

       (211, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),          -- in journal
       (212, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),          -- in journal
       (213, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),          -- in journal
       (214, 'business', 'business_plus', false, true, false, '2020-02-02T05:59:00+03:00'::timestamptz, now(), now(), now()),          -- in journal
       (215, 'business', 'business_plus', false, true, false, '2020-02-02T06:01:00+03:00'::timestamptz, now(), now(), now()),

       (216, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),
       (217, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),
       (218, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now()),
       (219, 'business', 'business_plus', false, true, false, '2020-02-02T15:00:00+03:00'::timestamptz, now(), now(), now());

INSERT INTO eats_place_subscriptions.places (place_id,
                                             business_type,
                                             country_code,
                                             timezone,
                                             region_id,
                                             created_at,
                                             inn)
-- Will not send billing info for places in UTC
-- For sending billing info will update tz in test body
VALUES (201, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (202, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (203, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (204, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (205, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),
       (206, 'restaurant', 'ru', 'UTC', 1, now(), '111111'),

       (207, 'restaurant', 'ru', 'UTC', 1, now(), '222222'),
       (208, 'restaurant', 'ru', 'UTC', 1, now(), '222222'),
       (209, 'restaurant', 'ru', 'UTC', 1, now(), NULL),
       (210, 'restaurant', 'ru', 'UTC', 1, now(), '222222'),
       (220, 'restaurant', 'ru', 'UTC', 1, now(), '222222'),

       (211, 'restaurant', 'ru', 'UTC', 1, now(), '333333'),
       (212, 'restaurant', 'ru', 'UTC', 1, now(), '333333'),
       (213, 'restaurant', 'ru', 'UTC', 1, now(), '333333'),
       (214, 'restaurant', 'ru', 'UTC', 1, now(), '333333'),
       (215, 'restaurant', 'ru', 'UTC', 1, now(), '333333'),

       (216, 'restaurant', 'ru', 'UTC', 1, now(), '444444'),
       (217, 'restaurant', 'ru', 'UTC', 1, now(), '555555'),
       (218, 'restaurant', 'ru', 'UTC', 1, now(), '666666'),
       (219, 'restaurant', 'ru', 'UTC', 1, now(), '666666');

INSERT INTO eats_place_subscriptions.notifications_journal (place_id, created_at)
VALUES (211, '2020-02-02T15:00:00+03:00'::timestamptz),
       (212, '2020-02-02T15:00:00+03:00'::timestamptz - interval '1 days'),
       (213, '2020-02-02T15:00:00+03:00'::timestamptz - interval '2 days'),
       (214, '2020-01-29T15:00:00+03:00'::timestamptz),
       (215, '2020-01-29T15:00:00+03:00'::timestamptz),
       (216, '2020-02-02T15:00:00+03:00'::timestamptz);

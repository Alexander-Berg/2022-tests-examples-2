INSERT INTO eats_place_subscriptions.subscriptions (place_id,
                                                    tariff,
                                                    is_partner_updated,
                                                    is_trial,
                                                    valid_until,
                                                    activated_at,
                                                    created_at,
                                                    updated_at)
VALUES (200, 'business_plus', false, false, now(), now(), now(), now()), -- empty INN
       (201, 'business_plus', false, false, now(), now(), now(), now()),

       (202, 'business_plus', false, false, now(), now(), now(), now()), -- 1 with INN

       (203, 'business_plus', false, false, now(), now(), now(), now()), -- 2 with INN
       (204, 'business_plus', false, false, now(), now(), now(), now()),

       (205, 'business_plus', false, false, now(), now(), now(), now()), -- 3 with INN
       (206, 'business_plus', false, false, now(), now(), now(), now()),
       (207, 'business_plus', false, false, now(), now(), now(), now()),

       (208, 'business_plus', false, false, now(), now(), now(), now()), -- 4 with INN
       (209, 'business_plus', false, false, now(), now(), now(), now()),
       (210, 'business_plus', false, false, now(), now(), now(), now()),
       (211, 'business_plus', false, false, now(), now(), now(), now()),

       (212, 'business_plus', false, false, now(), now(), now(), now()), -- 5 active with INN
       (213, 'business_plus', false, false, now(), now(), now(), now()),
       (214, 'business_plus', false, false, now(), now(), now(), now()),
       (215, 'business_plus', false, false, now(), now(), now(), now()),
       (216, 'business_plus', false, false, now(), now(), now(), now()),

       (217, 'business_plus', false, false, now(), now(), now(), now()), -- 5 active with INN, 1 not business_plus
       (218, 'business_plus', false, false, now(), now(), now(), now()),
       (219, 'business_plus', false, false, now(), now(), now(), now()),
       (220, 'business_plus', false, false, now(), now(), now(), now()),
       (221, 'business', false, false, now(), now(), now(), now()),

       (222, 'business_plus', false, false, now(), now(), now(), now()), -- 5 active with INN, 1 not valid
       (223, 'business_plus', false, false, now(), now(), now(), now()),
       (224, 'business_plus', false, false, now(), now(), now(), now()),
       (225, 'business_plus', false, false, now(), now(), now(), now()),
       (226, 'business_plus', false, false, '2010-01-01', now(), now(), now()),

       (227, 'business_plus', false, false, now(), now(), now(), now()), -- 5 active with INN, 1 is trial
       (228, 'business_plus', false, false, now(), now(), now(), now()),
       (229, 'business_plus', false, false, now(), now(), now(), now()),
       (230, 'business_plus', false, false, now(), now(), now(), now()),
       (231, 'business_plus', false, true, now(), now(), now(), now());

INSERT INTO eats_place_subscriptions.places (place_id,
                                             business_type,
                                             country_code,
                                             timezone,
                                             region_id,
                                             created_at,
                                             inn)
-- Will not send billing info for places in UTC
-- For sending billing info will update tz in test body
VALUES (200, 'restaurant', 'ru', 'UTC', 1, now(), null), -- empty INN
       (201, 'restaurant', 'ru', 'UTC', 1, now(), null),

       (202, 'restaurant', 'ru', 'UTC', 1, now(), '111111'), -- 1 with INN

       (203, 'restaurant', 'ru', 'UTC', 1, now(), '222222'), -- 2 with INN
       (204, 'restaurant', 'ru', 'UTC', 1, now(), '222222'),

       (205, 'restaurant', 'ru', 'UTC', 1, now(), '333333'), -- 3 with INN
       (206, 'restaurant', 'ru', 'UTC', 1, now(), '333333'),
       (207, 'restaurant', 'ru', 'UTC', 1, now(), '333333'),

       (208, 'restaurant', 'ru', 'UTC', 1, now(), '444444'), -- 4 with INN
       (209, 'restaurant', 'ru', 'UTC', 1, now(), '444444'),
       (210, 'restaurant', 'ru', 'UTC', 1, now(), '444444'),
       (211, 'restaurant', 'ru', 'UTC', 1, now(), '444444'),

       (212, 'restaurant', 'ru', 'UTC', 1, now(), '555555'), -- 5 active with INN
       (213, 'restaurant', 'ru', 'UTC', 1, now(), '555555'),
       (214, 'restaurant', 'ru', 'UTC', 1, now(), '555555'),
       (215, 'restaurant', 'ru', 'UTC', 1, now(), '555555'),
       (216, 'restaurant', 'ru', 'UTC', 1, now(), '555555'),

       (217, 'restaurant', 'ru', 'UTC', 1, now(), '666666'), -- 5 active with INN, 1 not business_plus
       (218, 'restaurant', 'ru', 'UTC', 1, now(), '666666'),
       (219, 'restaurant', 'ru', 'UTC', 1, now(), '666666'),
       (220, 'restaurant', 'ru', 'UTC', 1, now(), '666666'),
       (221, 'restaurant', 'ru', 'UTC', 1, now(), '666666'),

       (222, 'restaurant', 'ru', 'UTC', 1, now(), '777777'), -- 5 active with INN, 1 not valid
       (223, 'restaurant', 'ru', 'UTC', 1, now(), '777777'),
       (224, 'restaurant', 'ru', 'UTC', 1, now(), '777777'),
       (225, 'restaurant', 'ru', 'UTC', 1, now(), '777777'),
       (226, 'restaurant', 'ru', 'UTC', 1, now(), '777777'),

       (227, 'restaurant', 'ru', 'UTC', 1, now(), '888888'), -- 5 active with INN, 1 is trial
       (228, 'restaurant', 'ru', 'UTC', 1, now(), '888888'),
       (229, 'restaurant', 'ru', 'UTC', 1, now(), '888888'),
       (230, 'restaurant', 'ru', 'UTC', 1, now(), '888888'),
       (231, 'restaurant', 'ru', 'UTC', 1, now(), '888888');

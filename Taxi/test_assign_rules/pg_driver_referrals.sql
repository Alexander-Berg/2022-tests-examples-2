INSERT INTO settings
VALUES ('{
  "display_tab": true,
  "enable_stats_job": true,
  "generate_new_promocodes": true,
  "enable_payments_job": true,
  "enable_mapreduce_job": true,
  "enable_antifraud_job": true,
  "cities": [
    "Москва",
    "Тверь",
    "Санкт-Петербург"
  ]
}'::jsonb);

INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at)
VALUES ('r0', 'p0', 'd0', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),
       ('r1', 'p0', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'in_progress', '12e25ed671efab_3', '2018-01-01 12:00:00'),

       -- driver p3_d3 has 1 ride during gap in rules, NO RULE ASSIGNED
       ('r3', 'p3', 'd3', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),

       -- driver p4_d4 has 1 ride outside any zone, NO RULE ASSIGNED
       ('r4', 'p4', 'd4', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),

       -- driver p5_d5 has no rides TODAY, NO RULE ASSIGNED
       ('r5', 'p5', 'd5', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),

       -- driver p6_d6 has synced_orders in wrong order in DB
       ('r6', 'p6', 'd6', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),

       -- driver p7_d7 has synced_orders in wrong order in DB
       ('r7', 'p7', 'd7', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),


       -- parent driver for referrer_orders_providers testing
       ('r8', 'p8', 'd8', 'ПРОМОКОД2', NULL, 'completed', NULL, NULL),

       -- is not gonna be assigned because his rule.referrer_orders_providers
       -- doesn't match parent's orders_provider
       ('r9', 'p9', 'd9', NULL, 'ПРОМОКОД2', 'waiting_for_rule', NULL, NULL),

       -- driver who is going to be assigned successfully
       ('r10', 'p10', 'd10', NULL, 'ПРОМОКОД2', 'waiting_for_rule', NULL, NULL),

       -- is not gonna be assigned because his rule.referrer_orders_providers is empty
       ('r11', 'p11', 'd11', NULL, 'ПРОМОКОД2', 'waiting_for_rule', NULL, NULL),

       -- driver (courier) who will be matched by agglomeration
       ('r12', 'p12', 'd12', NULL, 'ПРОМОКОД2', 'waiting_for_rule', NULL, NULL);



INSERT INTO rules (id, start_time, end_time, tariff_zones, taxirate_ticket, currency,
                   referrer_bonus, referree_days, referree_rides, author,
                   orders_provider, tag, referrer_orders_providers, agglomerations)
VALUES ('12e25ed671efab_0', '2019-04-20 12:00:00', '2019-10-01 12:00:00',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-1', 'RUB', 500, 21, 1, 'andresokol',
        'taxi', NULL, ARRAY ['taxi'], ARRAY []::VARCHAR[]),
       ('12e25ed671efab_1', '2019-04-20 09:00:00', '2019-12-01 12:00:00',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-2', 'RUB', 5000, 14, 2, 'andresokol',
        'taxi', NULL, ARRAY ['taxi'], ARRAY []::VARCHAR[]),
       ('12e25ed671efab_2', '2018-01-01 12:00:00', '2018-02-01 12:00:00',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-2', 'RUB', 5000, 14, 3, 'andresokol',
        'taxi', NULL, ARRAY ['taxi'], ARRAY []::VARCHAR[]),

       -- gap in riga from 04:00 to 12:00
       ('12e25ed671efab_3', '2019-04-20 00:00:00', '2019-04-20 04:00:00',
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 4, 'andresokol', 'taxi',
        NULL, ARRAY ['taxi'], ARRAY []::VARCHAR[]),
       ('12e25ed671efab_4', '2019-04-20 12:00:00', '2019-10-01 12:00:00',
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 5, 'andresokol', 'taxi',
        NULL, ARRAY ['taxi'], ARRAY []::VARCHAR[]),

       ('12e25ed671efab_5', '2019-04-20 12:00:00', '2019-10-01 12:00:00',
        ARRAY ['ekb'], 'TAXIRATE-4', 'RUB', 500, 21, 1, 'rndr', 'eda',
        NULL, ARRAY ['eda'], ARRAY []::VARCHAR[]),
       ('12e25ed671efab_6', '2019-04-20 12:00:00', '2019-10-01 12:00:00',
        ARRAY ['ufa'], 'TAXIRATE-5', 'RUB', 500, 21, 1, 'rndr', 'eda',
        NULL, ARRAY []::VARCHAR[], ARRAY []::VARCHAR[]),
       ('12e25ed671efab_7', '2019-04-20 12:00:00', '2019-10-01 12:00:00',
        ARRAY ['moscow'], 'TAXIRATE-6', 'RUB', 500, 21, 1, 'a-garikhanov',
        'eda', NULL, ARRAY ['eda'], ARRAY ['br_moscow_adm']);



INSERT INTO synced_orders (order_id, park_id, driver_id, nearest_zone, orders_provider, created_at)
VALUES ('o1', 'p1', 'd1', 'moscow', 'taxi', '2019-04-20 00:01:00'),

       ('o2', 'p0', 'd0', 'karaganda', 'taxi', '2019-04-20 00:01:00'),
       ('o3', 'p0', 'd0', 'karaganda', 'taxi', '2019-04-20 00:01:00'),
       ('o4', 'p0', 'd0', 'moscow', 'taxi', '2019-04-19 00:00:00'),
       ('o5', 'p0', 'd0', 'moscow', 'taxi', '2019-04-20 10:00:00'),
       ('o6', 'p0', 'd0', 'riga', 'taxi', '2019-04-20 23:01:00'),

       ('o7', 'p3', 'd3', 'riga', 'taxi', '2019-04-20 11:01:00'),

       ('o8', 'p4', 'd4', 'tallinn', 'taxi', '2019-04-20 14:23:00'),

       ('o9', 'p5', 'd5', 'moscow', 'taxi', '2019-04-19 16:01:00'),
       ('o10', 'p5', 'd5', 'kaluga', 'taxi', '2019-04-19 16:01:00'),
       ('o11', 'p5', 'd5', 'moscow', 'taxi', '2019-04-19 16:01:00'),

       ('o12', 'p6', 'd6', 'moscow', 'taxi', '2019-04-20 14:00:00'),
       ('o13', 'p6', 'd6', 'moscow', 'taxi', '2019-04-20 10:00:00'),

       ('o16', 'p7', 'd7', 'moscow', 'taxi', '2019-04-20 10:00:00'),
       ('o17', 'p7', 'd7', 'moscow', 'taxi', '2019-04-20 10:00:00'),

       ('o18', 'p9', 'd9', 'ekb', 'taxi', '2019-04-20 21:00:00'),
       ('o19', 'p10', 'd10', 'ekb', 'eda', '2019-04-20 21:00:00'),
       ('o20', 'p11', 'd11', 'ufa', 'eda', '2019-04-20 21:00:00');


INSERT INTO synced_orders (order_id, park_id, driver_id, nearest_zone, created_at, tariff_class, orders_provider)
VALUES ('o14', 'p3', 'd3', 'moscow', '2019-04-20 00:01:00', 'comfort', 'taxi'),
       ('o15', 'p3', 'd3', 'moscow', '2019-04-20 00:02:00', 'econom', 'taxi');

INSERT INTO rules (id, start_time, end_time, tariff_zones, currency,
                   referree_days, author, created_at,
                   tariff_classes, budget, description, steps,
                   orders_provider, referrer_orders_providers)
VALUES ('rule_with_steps', '2019-01-01', '2019-10-01',
        ARRAY['moscow'], 'RUB', 50, 'vdovkin', '2019-01-01',
        ARRAY['econom'], 1000, 'Test rule',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": 100,
                        "reason": "invited_other_park",
                        "type": "payment"
                    },
                    {
                        "reason": "invited_same_park",
                        "series": "test_series",
                        "type": "promocode"
                    },
                    {
                        "amount": 200,
                        "reason": "invited_selfemployed",
                        "type": "payment"
                    }
                ],
                "rides": 1
            }'::jsonb,
            '{
                "rewards": [
                    {
                        "reason": "invited_same_park",
                        "series": "test_series",
                        "type": "promocode"
                    }
                ],
                "rides": 2
            }'::jsonb
        ],
        'taxi', ARRAY ['taxi']
);

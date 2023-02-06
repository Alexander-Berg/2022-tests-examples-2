INSERT INTO rules (id, start_time, end_time, tariff_zones, taxirate_ticket, currency,
                   referrer_bonus, referree_days, referree_rides, author, referrer_orders_providers)
VALUES ('rule1', '2019-01-01', '2019-10-01',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-1', 'RUB', 500, 21, 50, 'andresokol', ARRAY['taxi']),
       ('rule2', '2019-10-01', '2019-12-01',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-2', 'RUB', 5000, 14, 100, 'andresokol', ARRAY['taxi']),
       ('rule3', '2019-01-01', '2019-10-01',
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 10, 'andresokol', ARRAY['taxi']);

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
VALUES ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),
       ('r3', 'p3', 'd3', NULL, 'ПРОМОКОД1', 'in_progress', 'rule1', '2019-04-20'),
       ('r4', 'p4', 'd4', NULL, 'ПРОМОКОД1', 'in_progress', 'rule1', '2019-04-20'),
       ('r5', 'p5', 'd5', NULL, 'ПРОМОКОД1', 'failed', 'rule1', '2019-01-01'),
       ('r6', 'p6', 'd6', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule1', '2019-01-01');


INSERT INTO daily_stats (id, park_id, driver_id, date, rides_total, rides_accounted, is_frauder)
VALUES ('1', 'p3', 'd3', '2019-04-20', 10, 12, false),
       ('2', 'p3', 'd3', '2019-04-21', 10, 12, false),
       ('3', 'p3', 'd3', '2019-04-19', 10, 12, true),
       ('4', 'p4', 'd4', '2019-04-20', 2, 1, false),
       ('5', 'p5', 'd5', '2019-01-01', 2, 1, false),
       ('6', 'p6', 'd6', '2019-01-01', 300, 50, false),
       ('7', 'p7', 'd7', '2019-01-01', 4, 4, false),
       ('8', 'p8', 'd8', '2019-01-01', 1, 1, false),
       ('9', 'p9', 'd9', '2019-01-01', 2, 2, false);


INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r7', 'p7', 'd7', NULL, 'ПРОМОКОД1', 'completed', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 1),
        ('r8', 'p8', 'd8', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 0),
        ('r9', 'p9', 'd9', NULL, 'ПРОМОКОД1', 'awaiting_promocode', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_selfemployed', 1);

INSERT INTO rules (id, start_time, end_time, tariff_zones, currency,
                   referree_days, author, created_at,
                   tariff_classes, budget, description, steps, referrer_orders_providers)
VALUES ('rule_with_steps', '2019-01-01', '2019-10-01',
        ARRAY['moscow'], 'RUB', 21, 'vdovkin', '2019-01-01',
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
                        "reason": "invited_selfemployed",
                        "series": "test_series_2",
                        "type": "promocode"
                    }
                ],
                "rides": 2
            }'::jsonb,
            '{
                "rewards": [
                    {
                        "reason": "invited_other_park",
                        "amount": 200,
                        "type": "payment"
                    },
                    {
                        "reason": "invited_same_park",
                        "amount": 100,
                        "type": "payment"
                    }
                ],
                "rides": 3
            }'::jsonb
        ], ARRAY['taxi']
);

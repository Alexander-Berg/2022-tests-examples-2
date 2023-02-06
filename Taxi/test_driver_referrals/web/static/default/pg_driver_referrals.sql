INSERT INTO rules (id, start_time, end_time, orders_provider, referrer_orders_providers, tariff_zones, taxirate_ticket, currency,
                   referrer_bonus, referree_days, referree_rides, author, created_at)
VALUES ('12e25ed671efab_0', '2019-01-01', '2019-10-01', NULL, NULL,
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-1', 'RUB', 500, 21, 50, 'andresokol', '2019-01-01'),
       ('12e25ed671efab_1', '2019-10-01', '2019-12-01', NULL, NULL,
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-2', 'RUB', 5000, 14, 100, 'andresokol', '2019-01-01'),
       ('12e25ed671efab_3', '2019-01-01', '2019-10-01', NULL, NULL,
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 10, 'andresokol', '2019-01-01'),
       ('12e25ed671efab_4', '2019-01-01', '2019-10-01', 'taxi',  NULL,
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-4', 'RUB', 500, 21, 50, 'andresokol', '2019-01-01'),
       ('12e25ed671efab_5', '2019-01-01', '2019-10-01', 'eda', NULL,
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-5', 'RUB', 500, 21, 50, 'andresokol', '2019-01-01'),
       ('12e25ed671efab_6', '2019-01-01', '2019-10-01', 'taxi', ARRAY['taxi']::VARCHAR(32)[],
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-6', 'RUB', 500, 21, 50, 'andresokol', '2019-01-01'),
       ('12e25ed671efab_7', '2019-01-01', '2019-10-01', 'eda', ARRAY['eda']::VARCHAR(32)[],
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-7', 'RUB', 500, 21, 50, 'andresokol', '2019-01-01'),
       ('12e25ed671efab_8', '2019-01-01', '2019-10-01', 'taxi', ARRAY['eda']::VARCHAR(32)[],
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-8', 'RUB', 500, 21, 50, 'andresokol', '2019-01-01');

INSERT INTO rules (id, start_time, end_time, orders_provider, tariff_zones, currency,
                   referree_days, author, created_at,
                   tariff_classes, budget, description, steps)
VALUES ('rule_with_steps', '2019-01-01', '2019-10-01', NULL,
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
                        "amount": 100,
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
        ]
),
    ('rule_with_steps_taxi', '2019-01-01', '2019-10-01', 'taxi',
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
                        "amount": 100,
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
        ]
),
    ('rule_with_steps_eda', '2019-01-01', '2019-10-01', 'eda',
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
                        "amount": 100,
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
        ]
);

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
    "Санкт-Петербург",
    "Минск",
    "Рига"
  ]
}'::jsonb);


INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, created_at)
VALUES ('r0', 'p0', 'd0', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL, '2019-04-04'),
       ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL, '2019-01-01'),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'in_progress', '12e25ed671efab_3',
        '2019-04-20 19:34', '2019-04-20'),
       ('r3', 'p3eda', 'd3', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL, '2019-04-04');

INSERT INTO daily_stats (id, park_id, driver_id, date,
                         rides_total, rides_accounted, is_frauder)
VALUES ('ds1', 'p2', 'd2', '2019-04-20', 2, 1, NULL),
       ('ds2', 'p2', 'd2', '2019-04-21', 4, 3, true),
       ('ds3', 'p2', 'd2', '2019-04-22', 6, 5, false);

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
VALUES ('r0', 'p0', 'd0', NULL, 'ПРОМОКОД1', 'in_progress', 'r1', '2019-04-18 13:00:00'),
       ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'in_progress', 'r1', '2019-04-19 13:00:00'),
       ('r3', 'p3', 'd3', NULL, 'ПРОМОКОД1', 'in_progress', 'r1', '2019-04-17 13:00:00'),
       ('r4', 'p4', 'd4', NULL, 'ПРОМОКОД1', 'in_progress', 'r1', '2019-04-17 13:00:00'),
       ('r5', 'p5', 'd5', NULL, 'ПРОМОКОД1', 'in_progress', 'r1', '2019-04-17 13:00:00');


INSERT INTO rules (id, start_time, end_time, tariff_zones, taxirate_ticket, currency,
                   referrer_bonus, referree_days, referree_rides, author)
VALUES ('r1', '2019-04-01 00:00:00', '2019-10-01 12:00:00',
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 2, 'andresokol');


INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r6', 'p6', 'd6', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 0),
        ('r7', 'p7', 'd7', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_selfemployed', 1),
        ('r8', 'p8', 'd8', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_selfemployed', 0),
        ('r9', 'p9', 'd9', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_same_park', 0);

INSERT INTO rules (id, start_time, end_time, tariff_zones, currency,
                   referree_days, author, created_at,
                   tariff_classes, budget, description, steps)
VALUES ('rule_with_steps', '2019-01-01', '2019-10-01',
        ARRAY['moscow'], 'RUB', 2, 'vdovkin', '2019-01-01',
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
                        "reason": "invited_selfemployed",
                        "series": "test_series",
                        "type": "promocode"
                    }
                ],
                "rides": 1
            }'::jsonb,
            '{
                "rewards": [
                    {
                        "reason": "invited_other_park",
                        "series": "test_series",
                        "type": "promocode"
                    }
                ],
                "rides": 2
            }'::jsonb
        ]
);


INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, child_status, rule_id, started_rule_at, reward_reason, current_step)
VALUES  ('r91', 'p91', 'd91', NULL, 'ПРОМОКОД1', 'in_progress', NULL, 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_same_park', 0),
        ('r92', 'p92', 'd92', NULL, 'ПРОМОКОД1', 'awaiting_child_reward', 'awaiting_parent_reward', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_same_park', 0);

INSERT INTO rules (id, start_time, end_time, tariff_zones, currency,
                   referree_days, author, created_at,
                   tariff_classes, budget, description, steps)
VALUES ('rule_with_child_steps', '2019-01-01', '2019-10-01',
        ARRAY['moscow'], 'RUB', 2, 'vdovkin', '2019-01-01',
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
                        "reason": "invited_selfemployed",
                        "series": "test_series",
                        "type": "promocode"
                    }
                ],
                "child_rewards": [
                    {
                        "series": "test_series",
                        "reason": "invited_same_park",
                        "type": "promocode"
                    }
                ],
                "rides": 1
            }'::jsonb,
            '{
                "rewards": [
                    {
                        "reason": "invited_other_park",
                        "series": "test_series",
                        "type": "promocode"
                    }
                ],
                "rides": 2
            }'::jsonb
        ]
);


INSERT INTO daily_stats (id, park_id, driver_id, date,
                         rides_total, rides_accounted, is_frauder)
    -- p1_d1 has stats, not yet finished (fraud orders)
VALUES ('ds1', 'p1', 'd1', '2019-04-19', 1, 1, false),
       ('ds2', 'p1', 'd1', '2019-04-18', 9, 9, true),

       -- p2_d2 has started y-day, but already done
       ('ds3', 'p2', 'd2', '2019-04-19', 5, 5, false),

       -- p3_d3 should fail, no orders

       -- p4_d4 has finished just in time
       ('ds4', 'p4', 'd4', '2019-04-19', 1, 1, false),
       ('ds5', 'p4', 'd4', '2019-04-18', 1, 1, false),

       -- p5_d5 failed, because is a frauder
       ('ds6', 'p5', 'd5', '2019-04-19', 9, 9, true),
       ('ds7', 'p5', 'd5', '2019-04-18', 9, 9, true),

        -- p6_d6 has finished just in time
       ('ds8', 'p6', 'd6', '2019-04-19', 1, 1, false),
       ('ds9', 'p6', 'd6', '2019-04-18', 1, 1, false),

        -- p7_d7 has finished just in time
       ('ds10', 'p7', 'd7', '2019-04-19', 1, 1, false),
       ('ds11', 'p7', 'd7', '2019-04-18', 1, 1, false),

        -- p8_d8 has finished just in time
       ('ds12', 'p8', 'd8', '2019-04-19', 1, 1, false),
       ('ds13', 'p8', 'd8', '2019-04-18', 1, 1, false),

        -- p9_d9 has finished just in time
       ('ds14', 'p9', 'd9', '2019-04-19', 1, 1, false),
       ('ds15', 'p9', 'd9', '2019-04-18', 1, 1, false),

       -- p91_d91 has finished just in time
       ('ds16', 'p91', 'd91', '2019-04-19', 1, 1, false),
       ('ds17', 'p91', 'd91', '2019-04-18', 1, 1, false);

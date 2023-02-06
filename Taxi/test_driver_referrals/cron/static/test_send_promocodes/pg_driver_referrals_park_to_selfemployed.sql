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
                               status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL, NULL, 0),
       ('r6', 'p6', 'd6', NULL, 'ПРОМОКОД1', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 0),
        ('r7', 'p7', 'd7', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 1),
        ('r8', 'p8', 'd8', NULL, 'ПРОМОКОД1', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 1),
        ('r9', 'p9', 'd9', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 0);


INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, child_status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r91', 'p91', '91', NULL, 'ПРОМОКОД1', 'awaiting_promocode', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 1),
       ('r92', 'p92', '92', NULL, 'ПРОМОКОД1', 'in_progress', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 1),
       ('r93', 'p93', '93', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 1),
       ('r94', 'p94', '94', NULL, 'ПРОМОКОД1', 'awaiting_child_reward', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_selfemployed_from_park', 1);

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
                        "reason": "invited_selfemployed",
                        "series": "test_series",
                        "type": "promocode"
                    }
                ],
                "child_rewards": [
                    {
                        "series": "test_series",
                        "reason": "invited_selfemployed",
                        "type": "promocode"
                    }
                ],
                "rides": 1
            }'::jsonb,
            '{
                "rewards": [
                    {
                        "reason": "invited_selfemployed",
                        "series": "test_series_2",
                        "type": "promocode"
                    }
                ],
                "child_rewards": [
                    {
                        "series": "test_series_2",
                        "reason": "invited_selfemployed",
                        "type": "promocode"
                    }
                ],
                "rides": 2
            }'::jsonb
        ]
);

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
VALUES ('r0', 'p0', 'd0', NULL, 'ПРОМОКОД1', 'waiting_for_rule', 'rule_with_steps', NULL),
       ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, '2019-04-20 12:00:00'),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-20 12:00:00'),

       -- driver p3_d3 has 1 ride during gap in rules, NO RULE ASSIGNED
       ('r3', 'p3', 'd3', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-20 12:00:00'),

       -- driver p4_d4 has 1 ride outside any zone, NO RULE ASSIGNED
       ('r4', 'p4', 'd4', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-20 12:00:00');


INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r6', 'p6', 'd6', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 0),
        ('r7', 'p7', 'd7', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 1),
        ('r8', 'p8', 'd8', NULL, 'ПРОМОКОД1', 'awaiting_promocode', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 1),
        ('r9', 'p9', 'd9', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_same_park', 0),
        ('r93', 'p12', 'd12', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_kid_pay', '2019-04-17 13:00:00',
        'invited_other_park', 0);



INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, child_status, rule_id, started_rule_at, reward_reason, current_step)
VALUES  ('r91', 'p10', 'd10', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'awaiting_parent_reward', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_other_park', 1),
        ('r92', 'p11', 'd11', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_other_park', 1),
        ('r94', 'p11', 'scout_kid_id_1', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'awaiting_promocode', 'rule_with_child_steps', '2019-04-17 13:00:00',
        'invited_other_park', 1);

INSERT INTO rules (id, start_time, end_time, tariff_zones, currency,
                   referree_days, author, created_at,
                   tariff_classes, budget, description, steps, tag)
VALUES ('rule_with_child_steps', '2019-01-01', '2019-10-01',
        ARRAY['moscow'], 'RUB', 2, 'lordvoldemort', '2019-01-01',
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
                        "reason": "invited_other_park",
                        "series": "Some Series",
                        "type": "promocode"
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
                        "amount": 200,
                        "type": "payment"
                    }
                ],
                "child_rewards": [
                    {
                        "reason": "invited_other_park",
                        "series": "Some Series",
                        "type": "promocode"
                    }
                ],
                "rides": 2
            }'::jsonb
        ], 'scout'
);

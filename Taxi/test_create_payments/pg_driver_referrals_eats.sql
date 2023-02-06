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


INSERT INTO rules (
    id, start_time, end_time, tariff_zones, currency, orders_provider,
    referree_days, author, created_at, tariff_classes, budget, description,
    steps
)
VALUES (
    'rule_with_steps', '2019-01-01', '2019-10-01', ARRAY['moscow'], 'RUB', 'eda',
    2, 'author', '2019-01-01', ARRAY['econom'], 1000, 'Test rule',
    ARRAY[
        '{
            "rewards": [
                {
                    "amount": 100,
                    "reason": "invited_other_park",
                    "type": "payment"
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
            "rides": 2
        }'::jsonb
    ]
);


INSERT INTO referral_profiles (
    id, park_id, driver_id, promocode, invite_promocode, status, rule_id, started_rule_at, current_step
)
VALUES ('r0', 'p0', 'd0', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL, 0),
       ('r1', 'p1', 'd1', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL, 0),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-20 12:00:00', 0),
       ('r3', 'p3', 'd3', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-20 12:00:00', 1);

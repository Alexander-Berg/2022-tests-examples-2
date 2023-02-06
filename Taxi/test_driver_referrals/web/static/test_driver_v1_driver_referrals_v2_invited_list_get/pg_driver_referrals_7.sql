INSERT INTO rules (id, start_time, end_time, tariff_zones, currency, referree_days, author, created_at, tariff_classes, budget, description,
                steps, orders_provider, referrer_orders_providers)
VALUES
('rule_eda', '2019-01-01', '2019-12-31', ARRAY['moscow'], 'RUB', 21, 'namyotkin-ak', '2019-01-01', ARRAY[]::text[], 1000, 'Test rule 1',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": 100,
                        "reason": "invited_selfemployed",
                        "type": "payment"
                    }
                ],
                "rides": 1
            }'::jsonb
        ],
    'eda',
    ARRAY['taxi']
),
('rule_lavka', '2019-01-01', '2019-12-31', ARRAY['moscow'], 'RUB', 21, 'namyotkin-ak', '2019-01-01', ARRAY[]::text[], 1000, 'Test rule 2',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": 100,
                        "reason": "invited_selfemployed",
                        "type": "payment"
                    }
                ],
                "rides": 1
            }'::jsonb
        ],
    'lavka',
    ARRAY['taxi']
);

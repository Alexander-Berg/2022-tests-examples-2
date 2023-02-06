INSERT INTO rules (id, start_time, end_time, tariff_zones, currency, referree_days, author, created_at, tariff_classes, budget, description,
                steps, referrer_orders_providers)
VALUES
('rule_1', '2019-01-01', '2019-12-31', ARRAY['moscow'], 'RUB', 21, 'e-ovcharenko', '2019-01-01', ARRAY[]::text[], 1000, 'Test rule 1',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": 100,
                        "reason": "invited_same_park",
                        "type": "payment"
                    }
                ],
                "rides": 1
            }'::jsonb
        ], ARRAY['taxi']
),
('rule_2', '2019-01-01', '2019-12-31', ARRAY['moscow'], 'RUB', 21, 'e-ovcharenko', '2019-01-02', ARRAY['econom', 'business'], 1000, 'Test rule 1',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": 200,
                        "reason": "invited_same_park",
                        "type": "payment"
                    }
                ],
                "rides": 2
            }'::jsonb
        ], ARRAY['taxi']
),
('rule_3', '2019-01-01', '2019-12-31', ARRAY['moscow'], 'RUB', 21, 'e-ovcharenko', '2019-01-03', ARRAY['vip'], 1000, 'Test rule 1',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": 200,
                        "reason": "invited_same_park",
                        "type": "payment"
                    }
                ],
                "rides": 2
            }'::jsonb
        ], ARRAY['taxi']
);

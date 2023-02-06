INSERT INTO rules (id, start_time, end_time, tariff_zones, currency, referree_days, author, created_at, tariff_classes, budget, description,
                steps, referrer_orders_providers)
VALUES
('rule_econom', '2019-01-01', '2019-12-31', ARRAY['moscow'], 'RUB', 21, 'e-ovcharenko', '2019-01-01', ARRAY['econom'], 1000, 'Test rule 1',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": 100,
                        "reason": "invited_same_park",
                        "type": "payment"
                    },
                    {
                        "amount": 200,
                        "reason": "invited_other_park",
                        "type": "payment"
                    },
                    {
                        "amount": 300,
                        "reason": "invited_selfemployed",
                        "type": "payment"
                    }
                ],
                "rides": 5
            }'::jsonb,
            '{
                "rewards": [
                    {
                        "amount": 400,
                        "reason": "invited_same_park",
                        "type": "payment"
                    },
                    {
                        "amount": 500,
                        "reason": "invited_other_park",
                        "type": "payment"
                    }
                ],
                "rides": 10
            }'::jsonb
        ], ARRAY['taxi']
),
('rule_econom_later', '2019-01-01', '2019-12-31', ARRAY['moscow'], 'RUB', 21, 'e-ovcharenko', '2019-01-02', ARRAY['econom'], 1000, 'Test rule 2',
        ARRAY[
            '{
                "rewards": [
                    {
                        "amount": "1100",
                        "reason": "invited_same_park",
                        "type": "payment"
                    },
                    {
                        "amount": 1200,
                        "reason": "invited_other_park",
                        "type": "payment"
                    },
                    {
                        "amount": "1300",
                        "reason": "invited_selfemployed",
                        "type": "payment"
                    }
                ],
                "rides": 5
            }'::jsonb,
            '{
                "rewards": [
                    {
                        "amount": 1400,
                        "reason": "invited_same_park",
                        "type": "payment"
                    },
                    {
                        "amount": 1500,
                        "reason": "invited_other_park",
                        "type": "payment"
                    }
                ],
                "rides": 10
            }'::jsonb
        ], ARRAY['taxi']
);

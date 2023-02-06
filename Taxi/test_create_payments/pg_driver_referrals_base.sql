INSERT INTO rules (
    id,
    start_time,
    end_time,
    tariff_zones,
    currency,
    referree_days,
    author,
    created_at,
    tariff_classes,
    budget,
    description,
    steps
)
VALUES (
    'rule_with_steps',
    '2019-01-01',
    '2019-10-01',
    ARRAY ['moscow'],
    'RUB',
    2,
    'vdovkin',
    '2019-01-01',
    ARRAY ['econom'],
    1000,
    'Test rule',
    ARRAY [
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
                    "amount": 200,
                    "type": "payment"
                }
            ], 
            "rides": 2 
        }'::jsonb
    ]
),(
    'rule_with_kid_pay', 
    '2019-01-01',
    '2019-10-01',
    ARRAY ['moscow'],
    'RUB',
    2,
    'vdovkin',
    '2019-01-01',
    ARRAY ['econom'],
    1000,
    'Test rule with child pay',
    ARRAY[
        '{
            "rewards": [],
            "child_rewards" :[
                {
                    "reason": "invited_other_park",
                    "amount": 200,
                    "type": "payment"
                }
            ], 
            "rides": 1 } '::jsonb ]
);

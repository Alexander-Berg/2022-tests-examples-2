INSERT INTO hiring_tariffs.subscriptions_periods(
    "id",
    "subscription_id",
    "status",
    "starts_at",
    "ends_at"
) VALUES (
    1,
    'SUB_ID1',
    'inited',
    '2021-01-01',
    '2021-01-02'
),
(
    2,
    'SUB_ID2',
    'inited',
    '2021-01-01',
    '2021-01-02'
);


INSERT INTO hiring_tariffs.subscriptions(
    "id",
    "subscriber_id",
    "extra",
    "autoprolong",
    "city",
    "leads_count",
    "leads_type",
    "cost",
    "period_days"
) VALUES (
    'SUB_ID1',
    'SUBSCRIBER_ID1',
    '{}'::JSONB,
    TRUE,
    'Moscow',
    30,
    'rent',
    400.0,
    30
),
(
    'SUB_ID2',
    'SUBSCRIBER_ID2',
    '{}'::JSONB,
    TRUE,
    'Moscow',
    30,
    'rent',
    400.0,
    30
);

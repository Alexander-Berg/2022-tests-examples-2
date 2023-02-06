INSERT INTO signalq_billing.payments_info
(
    park_id,
    payment_progress, 
    payments_date,
    payment_amount,
    created_at,
    updated_at 
)
VALUES
(
    'p1',
    'in_progress',
    '2021-10-01',
    '0.2423',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'p2',
    'not_created',
    '2021-10-01',
    '60.0000', -- amount per one 3
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'p3',
    'not_created',
    '2021-10-01',
    '80.0000', -- amount per one 40
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'p4',
    'not_created',
    '2021-10-01',
    '160.0000', -- amount per one 40
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'p5',
    'not_created',
    '2021-10-01',
    '500.0000', -- amount per one 500
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'p5',
    'not_created',
    '2021-11-01',
    '4223.2423',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);


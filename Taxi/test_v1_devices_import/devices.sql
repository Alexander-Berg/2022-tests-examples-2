INSERT INTO signalq_billing.salesforce_opportunities (
    opportunity_id,
    is_b2b,
    park_id,
    tin,
    devices_count,
    close_datetime,
    non_paid_period_days
) VALUES (
    'op1',
    TRUE,
    NULL,
    'TIN1',
    4,
    '2021-12-12T00:00:00+03:00',
    365
),
(
    'op2',
    FALSE,
    'park_id2',
    NULL,
    5,
    '2021-11-12T00:00:00+03:00',
    90
),
(
    'op3',
    FALSE,
    'park_id2',
    NULL,
    2,
    '2021-11-12T00:00:00+03:00',
    90
);

INSERT INTO signalq_billing.billing_devices (
    serial_number,
    opportunity_id
) VALUES (
    'ABCDEFabcdef1',
    'op1'
),
(
    'ABCDEFabcdef2',
    'op1'
),
(
    'ABCDEFabcdef3',
    'op1'
),
(
    'ABCDEFabcdef9',
    'op2'
),
(
    'AAADEFabcdef1',
    'op3'
);

-- Postgresql insert migration does not work in testsuite
INSERT INTO signalq_billing.salesforce_auth_token (
    auth_token, updated_at
) VALUES (
    '', '2020-01-01T00:00:00+00:00'
);

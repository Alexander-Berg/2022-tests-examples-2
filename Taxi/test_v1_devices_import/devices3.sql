INSERT INTO signalq_billing.salesforce_opportunities (
    opportunity_id,
    is_b2b,
    park_id,
    tin,
    devices_count,
    close_datetime,
    non_paid_period_days
) VALUES (
    'op2',
    TRUE,
    NULL,
    'tin2',
    12,
    NULL,
    NULL
);

INSERT INTO signalq_billing.billing_devices (
    serial_number,
    opportunity_id
) VALUES (
    'AAADEFabcdef4',
    'op2'
);

-- Postgresql insert migration does not work in testsuite
INSERT INTO signalq_billing.salesforce_auth_token (
    auth_token, updated_at
) VALUES (
    '', '2020-01-01T00:00:00+00:00'
);

-- Postgresql insert migration does not work in testsuite
INSERT INTO signalq_billing.salesforce_auth_token (
    auth_token, updated_at
) VALUES (
    '', '2020-01-01T00:00:00+00:00'
);

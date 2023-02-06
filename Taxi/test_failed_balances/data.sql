INSERT INTO
    parks.balances_queue (billing_kwargs, fail_count)
VALUES
    (ROW('12345')::BALANCES_BILLING_KWARGS, 5),  -- max fail count is not reached
    (ROW('67890')::BALANCES_BILLING_KWARGS, 10); -- max fail count is reached


INSERT INTO
    parks.balances_queue_v2 (billing_kwargs, fail_count)
VALUES
    (ROW(12345, 111)::BALANCES_V2_BILLING_KWARGS, 5),  -- max fail count is not reached
    (ROW(67890, 111)::BALANCES_V2_BILLING_KWARGS, 10); -- max fail count is reached

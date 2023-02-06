INSERT INTO
    parks.balances_queue (billing_kwargs, fail_count, updated)
VALUES
    (ROW('1')::BALANCES_BILLING_KWARGS, 11, (clock_timestamp() at time zone 'utc')::timestamp - interval '1 hour'),
    (ROW('2')::BALANCES_BILLING_KWARGS, 10, (clock_timestamp() at time zone 'utc')::timestamp - interval '1 hour'),
    (ROW('3')::BALANCES_BILLING_KWARGS, 10, (clock_timestamp() at time zone 'utc')::timestamp - interval '4 hour'),
    (ROW('4')::BALANCES_BILLING_KWARGS, 9, (clock_timestamp() at time zone 'utc')::timestamp - interval '1 hour');

INSERT INTO
    parks.contracts_queue (billing_kwargs, fail_count, updated)
VALUES
    (ROW('5', 'SPENDABLE')::CONTRACTS_BILLING_KWARGS, 11, (clock_timestamp() at time zone 'utc')::timestamp - interval '1 hour');

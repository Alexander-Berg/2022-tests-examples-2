INSERT INTO
    parks.balances_queue (billing_kwargs)
VALUES
    (ROW('123456')::BALANCES_BILLING_KWARGS),
    (ROW('654321')::BALANCES_BILLING_KWARGS),
    (ROW('111111')::BALANCES_BILLING_KWARGS),
    (ROW('222222')::BALANCES_BILLING_KWARGS);

INSERT INTO parks.contract_versions (
    "ID",
    client_id,
    type,
    status,
    created,
    updated,
    "IS_ACTIVE"
)
VALUES (
    123456,
    '1',
    'GENERAL',
    'ACTIVE',
    (clock_timestamp() at time zone 'utc')::timestamp,
    (clock_timestamp() at time zone 'utc')::timestamp,
    1
),
(
     654321,
    '1',
    'GENERAL',
    'ACTIVE',
    (clock_timestamp() at time zone 'utc')::timestamp,
    (clock_timestamp() at time zone 'utc')::timestamp,
    1
),
(
    222222,
    '1',
    'GENERAL',
    'ACTIVE',
    (clock_timestamp() at time zone 'utc')::timestamp,
    (clock_timestamp() at time zone 'utc')::timestamp,
    0
);

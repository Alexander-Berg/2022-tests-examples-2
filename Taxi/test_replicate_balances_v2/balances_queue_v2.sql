INSERT INTO
    parks.balances_queue_v2 (billing_kwargs)
VALUES
    (ROW('123456', 111)::BALANCES_V2_BILLING_KWARGS),
    (ROW('654321', 111)::BALANCES_V2_BILLING_KWARGS),
    (ROW('111111', 111)::BALANCES_V2_BILLING_KWARGS),
    (ROW('222222', 111)::BALANCES_V2_BILLING_KWARGS);

INSERT INTO parks.contract_versions (
    "ID",
    client_id,
    type,
	"SERVICES",
    status,
    created,
    updated,
    "IS_ACTIVE"
)
VALUES (
    123456,
    '1',
    'GENERAL',
	ARRAY[111],
    'ACTIVE',
    (clock_timestamp() at time zone 'utc')::timestamp,
    (clock_timestamp() at time zone 'utc')::timestamp,
    1
),
(
     654321,
    '1',
    'GENERAL',
	ARRAY[111],
    'ACTIVE',
    (clock_timestamp() at time zone 'utc')::timestamp,
    (clock_timestamp() at time zone 'utc')::timestamp,
    1
),
(
    222222,
    '1',
    'GENERAL',
	ARRAY[111],
    'ACTIVE',
    (clock_timestamp() at time zone 'utc')::timestamp,
    (clock_timestamp() at time zone 'utc')::timestamp,
    0
);

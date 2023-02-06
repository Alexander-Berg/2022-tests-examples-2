INSERT INTO parks.contracts_queue(
    billing_kwargs
)
VALUES
    (ROW('client_id', 'GENERAL')::CONTRACTS_BILLING_KWARGS),
    (ROW('client_id2', 'GENERAL')::CONTRACTS_BILLING_KWARGS);


INSERT INTO parks.contract_versions(
    "ID",
    client_id,
    type,
	"SERVICES",
    "IS_CANCELLED",
    "IS_ACTIVE",
    status,
    created,
    updated
)
VALUES
    (1, 'client_id', 'GENERAL', ARRAY[111], 0, 1, 'ACTIVE', clock_timestamp(), clock_timestamp()),
    (2, 'client_id', 'GENERAL', ARRAY[111], 0, 1, 'ACTIVE', clock_timestamp(), clock_timestamp()),
    (3, 'client_id', 'GENERAL', ARRAY[111], 0, 1, 'INACTIVE', clock_timestamp(), clock_timestamp());


INSERT INTO
    parks.balances_queue (billing_kwargs)
VALUES
    (ROW(1)::BALANCES_BILLING_KWARGS),
    (ROW(2)::BALANCES_BILLING_KWARGS);


INSERT INTO
    parks.balances_queue_v2 (billing_kwargs)
VALUES
    (ROW(1, 111)::BALANCES_V2_BILLING_KWARGS),
    (ROW(2, 111)::BALANCES_V2_BILLING_KWARGS);

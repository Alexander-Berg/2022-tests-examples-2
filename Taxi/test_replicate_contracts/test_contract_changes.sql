INSERT INTO parks.contracts_queue(
    billing_kwargs
)
VALUES
    (ROW('client_id', 'GENERAL')::CONTRACTS_BILLING_KWARGS);


INSERT INTO parks.contract_versions(
    "ID",
    client_id,
    type,
    "IS_SIGNED",
    status,
    created,
    updated
)
VALUES
    (1, 'client_id', 'GENERAL', 0, 'INACTIVE', clock_timestamp(), clock_timestamp()),
    (2, 'client_id', 'GENERAL', 0, 'ACTIVE', clock_timestamp(), clock_timestamp()),
    (3, 'client_id', 'GENERAL', 0, 'ACTIVE', clock_timestamp(), clock_timestamp()),
    (4, 'client_id', 'GENERAL', 1, 'ACTIVE', clock_timestamp(), clock_timestamp()),
    (5, 'client_id', 'GENERAL', 1, 'ACTIVE', clock_timestamp(), clock_timestamp()),
    (6, 'client_id', 'GENERAL', 1, 'ACTIVE', clock_timestamp(), clock_timestamp()),
    (6, 'client_id', 'GENERAL', 1, 'ACTIVE', clock_timestamp(), clock_timestamp());


INSERT INTO
    parks.balances_queue (billing_kwargs)
VALUES
    (ROW('2')::BALANCES_BILLING_KWARGS),
    (ROW('3')::BALANCES_BILLING_KWARGS),
    (ROW('6')::BALANCES_BILLING_KWARGS);

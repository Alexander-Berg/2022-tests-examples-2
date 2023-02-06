INSERT INTO parks.contracts_queue(
    billing_kwargs
)
VALUES
    (ROW('client_id', 'GENERAL')::CONTRACTS_BILLING_KWARGS);

INSERT INTO parks.contract_versions(
    "ID",
    client_id,
    type,
    "IS_CANCELLED",
    "IS_ACTIVE",
    status,
    created,
    updated,
    "ATTRIBUTES_HISTORY"
)
VALUES
    (1, 'client_id', 'GENERAL', 0, 1, 'ACTIVE', clock_timestamp(), clock_timestamp(), '{"SERVICES": [["2020-01-01 00:00:00", [111]], ["2099-01-01 00:00:00", [111, 128]]]}'),
    (2, 'client_id', 'GENERAL', 0, 1, 'ACTIVE', clock_timestamp(), clock_timestamp(), NULL);

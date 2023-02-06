INSERT INTO
    parks.contracts_queue (billing_kwargs, fail_count, updated)
VALUES
    (ROW('5', 'SPENDABLE')::CONTRACTS_BILLING_KWARGS, 0, CAST('2020-04-13 14:05:00.000000' AS TIMESTAMP));

INSERT INTO parks.persons_queue (billing_kwargs, fail_count,  updated) VALUES
      (ROW('11')::PERSONS_BILLING_KWARGS, 0, CAST('2020-04-13 14:05:00.000000' AS TIMESTAMP));

INSERT INTO
    parks.balances_queue (billing_kwargs, fail_count, updated)
VALUES
    (ROW('5')::BALANCES_BILLING_KWARGS, 0, CAST('2020-04-13 14:05:00.000000' AS TIMESTAMP));

INSERT INTO corp.acts_queue (billing_kwargs, fail_count,  updated) VALUES
      (ROW('10'), 0, CAST('2020-04-13 14:05:00.000000' AS TIMESTAMP));

INSERT INTO parks.clients (id, park_id, created, updated)
VALUES (
    'client_id_1',
    'park_1',
    clock_timestamp(),
    clock_timestamp()
),
(
    'client_id_2',
    'park_2',
    clock_timestamp(),
    clock_timestamp()
);

ALTER TABLE parks.contract_versions DISABLE TRIGGER parks_contract_versions_ins_tr;

INSERT INTO parks.contract_versions(
    "ID",
    version,
    client_id,
    type,
    created,
    updated,
    expired
)
VALUES (
    1, 1, 'client_id_1', 'GENERAL',
    CAST('2020-04-13 14:05:00.000000' AS TIMESTAMP),
    CAST('2020-04-13 14:15:00.000000' AS TIMESTAMP),
    NULL
),
(
    2, 1, 'client_id_1', 'GENERAL',
    CAST('2020-04-13 14:02:00.000000' AS TIMESTAMP),
    CAST('2020-04-13 14:15:00.000000' AS TIMESTAMP),
    CAST('2020-04-13 14:10:00.000000' AS TIMESTAMP)
),
(
    2, 2, 'client_id_1', 'GENERAL',
    CAST('2020-04-13 14:10:00.000000' AS TIMESTAMP),
    CAST('2020-04-13 14:15:00.000000' AS TIMESTAMP),
    NULL
);

ALTER TABLE parks.contract_versions ENABLE TRIGGER parks_contract_versions_ins_tr;

INSERT INTO parks.persons (
    "ID",
    "CLIENT_ID",
    created,
    updated
)
VALUES (
    1,
    'client_id_1',
    CAST('2020-04-13 14:06:00.000000' AS TIMESTAMP),
    clock_timestamp()
),
(
    2,
    'client_id_2',
    CAST('2020-04-13 14:08:00.000000' AS TIMESTAMP),
    clock_timestamp()
);

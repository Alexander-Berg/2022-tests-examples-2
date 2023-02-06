INSERT INTO
    parks.clients (id, park_id, created, updated)
VALUES
    (
     '123456',
     '1',
     '2016-03-16T09:00:00.000000+00:00'::timestamp,
     '2016-03-16T09:00:00.000000+00:00'::timestamp
     );

INSERT INTO parks.contracts_queue(
    billing_kwargs
)
VALUES
    (ROW('123456', 'GENERAL')::CONTRACTS_BILLING_KWARGS),
    (ROW('123456', 'SPENDABLE')::CONTRACTS_BILLING_KWARGS);

INSERT INTO parks.persons_queue(
    billing_kwargs
)
VALUES
    (ROW('123456')::PERSONS_BILLING_KWARGS);

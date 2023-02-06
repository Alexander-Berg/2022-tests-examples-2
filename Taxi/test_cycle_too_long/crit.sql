INSERT INTO parks.persons_queue (billing_kwargs, updated) VALUES
    (ROW('10'), CAST('2017-01-01 10:00:00.000002' AS TIMESTAMP));

INSERT INTO parks.contracts_queue (billing_kwargs, updated) VALUES
    (ROW('16', 'GENERAL'), CAST('2017-01-01 10:00:00.000002' AS TIMESTAMP));

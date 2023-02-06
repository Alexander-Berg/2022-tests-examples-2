INSERT INTO parks.persons_queue (billing_kwargs, updated) VALUES
      (ROW('10'), CAST('2017-01-01 09:10:00.000001' AS TIMESTAMP));

INSERT INTO parks.contracts_queue (billing_kwargs, updated) VALUES
    (ROW('16', 'SPENDABLE'), CAST('2017-01-01 10:59:00.000002' AS TIMESTAMP));

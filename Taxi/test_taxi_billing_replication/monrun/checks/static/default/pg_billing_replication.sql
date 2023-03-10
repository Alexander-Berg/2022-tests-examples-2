INSERT INTO parks.persons_queue (billing_kwargs, updated) VALUES
    (ROW('1'), CAST('2017-01-01 08:58:00.000001' AS TIMESTAMP)),
    (ROW('2'), CAST('2017-01-01 08:40:00.000001' AS TIMESTAMP)),
    (ROW('3'), CAST('2017-01-01 08:30:00.000001' AS TIMESTAMP)),
    (ROW('4'), CAST('2017-01-01 08:20:00.000001' AS TIMESTAMP)),
    (ROW('5'), CAST('2017-01-01 08:10:00.000001' AS TIMESTAMP)),
    (ROW('6'), CAST('2017-01-01 08:00:00.000001' AS TIMESTAMP)),
    (ROW('7'), CAST('2017-01-01 07:30:00.000001' AS TIMESTAMP)),
    (ROW('8'), CAST('2017-01-01 07:00:00.000001' AS TIMESTAMP)),
    (ROW('9'), CAST('2017-01-01 06:00:00.000001' AS TIMESTAMP));

INSERT INTO parks.contracts_queue (billing_kwargs, updated) VALUES
    (ROW('1', 'SPENDABLE'), CAST('2017-01-01 09:02:00.000001' AS TIMESTAMP)),
    (ROW('2', 'SPENDABLE'), CAST('2017-01-01 09:00:00.000001' AS TIMESTAMP)),
    (ROW('3', 'GENERAL'), CAST('2017-01-01 08:40:00.000001' AS TIMESTAMP)),
    (ROW('4', 'GENERAL'), CAST('2017-01-01 08:20:00.000001' AS TIMESTAMP)),
    (ROW('5', 'GENERAL'), CAST('2017-01-01 08:10:00.000001' AS TIMESTAMP)),
    (ROW('6', 'SPENDABLE'), CAST('2017-01-01 08:00:00.000001' AS TIMESTAMP)),
    (ROW('7', 'GENERAL'), CAST('2017-01-01 07:45:00.000001' AS TIMESTAMP)),
    (ROW('8', 'SPENDABLE'), CAST('2017-01-01 07:35:00.000001' AS TIMESTAMP)),
    (ROW('9', 'GENERAL'), CAST('2017-01-01 07:25:00.000001' AS TIMESTAMP)),
    (ROW('10', 'GENERAL'), CAST('2017-01-01 07:15:00.000001' AS TIMESTAMP)),
    (ROW('11', 'GENERAL'), CAST('2017-01-01 07:00:00.000001' AS TIMESTAMP)),
    (ROW('12', 'SPENDABLE'), CAST('2017-01-01 06:50:00.000001' AS TIMESTAMP)),
    (ROW('13', 'GENERAL'), CAST('2017-01-01 05:20:00.000001' AS TIMESTAMP)),
    (ROW('14', 'SPENDABLE'), CAST('2017-01-01 05:10:00.000001' AS TIMESTAMP)),
    (ROW('15', 'GENERAL'), CAST('2017-01-01 05:00:00.000001' AS TIMESTAMP));

INSERT INTO parks.persons ("ID", created, updated, revision, status) VALUES
    ('1', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 11:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('2', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:59:00.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('3', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:58:00.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('4', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:57:40.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('5', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:57:20.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('6', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:57:00.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('7', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:56:30.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('8', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('9', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 09:50:00.000001' AS TIMESTAMP), 1, 'ACTIVE'),
    ('10', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 09:42:00.000001' AS TIMESTAMP), 1, 'ACTIVE');

ALTER TABLE parks.contract_versions DISABLE TRIGGER parks_contract_versions_ins_tr;

INSERT INTO parks.contract_versions ("ID", client_id, type, created, updated, revision, status, version) VALUES
    (1, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 11:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (2, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 11:59:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (3, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (4, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (5, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (6, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (7, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (8, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (9, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1),
    (10, '1', 'GENERAL', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), 1, 'ACTIVE', 1);

ALTER TABLE parks.contract_versions ENABLE TRIGGER parks_contract_versions_ins_tr;

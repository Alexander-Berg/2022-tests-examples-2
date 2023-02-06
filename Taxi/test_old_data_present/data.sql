INSERT INTO parks.clients (id, park_id, created, updated) VALUES
    ('1', '2', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2018-01-21 9:00:00.000001' AS TIMESTAMP));

INSERT INTO parks.balances ("ContractID", created, updated) VALUES
    (1, CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2018-01-25 9:00:01.000000' AS TIMESTAMP));

INSERT INTO parks.contract_field_diffs (id, field, before, after, timestamp) VALUES
    (974849, 'CONTRACT_TYPE', 'None', '81', CAST('2018-01-21 7:00:00.000001' AS TIMESTAMP));

INSERT INTO parks.contract_changes (id, type, timestamp) VALUES
    (826684, 'deactivation', CAST('2018-01-27 9:00:00.000001' AS TIMESTAMP));

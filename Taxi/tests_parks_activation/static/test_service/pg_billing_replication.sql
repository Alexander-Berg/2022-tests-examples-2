INSERT INTO parks.clients (id, park_id, created, updated) VALUES
    ('103917439', '100', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP)),
    ('105352633', '200', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP)),
    ('105391493', '300', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP)),
    ('105423433', '300', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP));


INSERT INTO parks.contracts ("ID", client_id, type, "IS_ACTIVE", "CURRENCY", "NETTING", "SERVICES", created, updated, status, "CONTRACT_TYPE") VALUES (
    553918, '103917439', 'GENERAL', 1, 'RUR', 1, '{128,124,125,605,111}', '2018-09-26 00:00:00', '2019-03-05 10:56:24.664433',
    'ACTIVE', NULL
);
INSERT INTO parks.contracts ("ID", client_id, type, "IS_ACTIVE", "CURRENCY", "NETTING", "SERVICES", created, updated, status, "CONTRACT_TYPE") VALUES (
    553919, '103917439', 'SPENDABLE', 0, 'RUR', NULL, '{135}','2019-03-05 10:56:24', '2018-09-26 00:00:00',
    'ACTIVE', 85
);
INSERT INTO parks.contracts ("ID", client_id, type, "IS_ACTIVE", "CURRENCY", "NETTING", "SERVICES", created, updated, status, "CONTRACT_TYPE") VALUES (
    553920, '103917439', 'SPENDABLE', 1, 'RUR', NULL, '{137}', '2018-09-26 00:00:00', '2019-03-05 10:56:24.664433',
    'ACTIVE', 81
);
INSERT INTO parks.contracts ("ID", client_id, type, "IS_ACTIVE", "CURRENCY", "NETTING", "SERVICES", created, updated, status, "CONTRACT_TYPE") VALUES (
    1009627, '105352633', 'GENERAL', 1, 'RUR', 1, '{128,111,124,125,605}', '2018-12-25 00:00:00', '2019-03-05 10:56:24.664433',
    'INACTIVE', NULL
);
INSERT INTO parks.contracts ("ID", client_id, type, "IS_ACTIVE", "CURRENCY", "NETTING", "SERVICES", created, updated, status, "CONTRACT_TYPE") VALUES (
    1040309, '105423433', 'SPENDABLE', 1, 'RUR', NULL, '{128,605,626,111,124,125}', '2018-12-28 00:00:00',
    '2019-03-05 10:56:24.664433', 'INACTIVE', 87
);


INSERT INTO parks.balances ("ContractID", "Balance", "CurrMonthCharge", "CommissionToPay", "CurrMonthBonus", "BonusLeft", "ClientID", "OfferAccepted", "Currency", "NettingLastDt", "PersonalAccountExternalID", "DT", "created", "updated", "revision") VALUES (553918, '0', '0', NULL, '0', '0', 103917439, 1, 'RUB', NULL, 'ЛСТ-1259357521-1', '2019-03-15 15:46:59.315361', '2019-02-27 16:43:43.269676', '2019-03-15 12:46:58.996166', 1);
INSERT INTO parks.balances ("ContractID", "Balance", "CurrMonthCharge", "CommissionToPay", "CurrMonthBonus", "BonusLeft", "ClientID", "OfferAccepted", "Currency", "NettingLastDt", "PersonalAccountExternalID", "DT", "created", "updated", "revision") VALUES (553920, '10000', '0', NULL, '0', '0', 104871401, NULL, 'RUB', NULL, 'ЛСТ-1261397230-1', '2019-03-15 15:46:59.312176', '2019-02-20 19:10:59.334911', '2019-03-15 12:46:58.996166', 2);
INSERT INTO parks.balances ("ContractID", "Balance", "CurrMonthCharge", "CommissionToPay", "CurrMonthBonus", "BonusLeft", "ClientID", "OfferAccepted", "Currency", "NettingLastDt", "PersonalAccountExternalID", "DT", "created", "updated", "revision") VALUES (1009624, '0', '0', NULL, '0', '0', 105352630, 1, 'RUB', NULL, 'ЛСТ-1262707106-1', '2019-02-20 23:32:37.772052', '2019-02-20 19:10:59.334911', '2019-02-20 20:32:37.700099', 3);
INSERT INTO parks.balances ("ContractID", "Balance", "CurrMonthCharge", "CommissionToPay", "CurrMonthBonus", "BonusLeft", "ClientID", "OfferAccepted", "Currency", "NettingLastDt", "PersonalAccountExternalID", "DT", "created", "updated", "revision") VALUES (1009627, '0', '0', NULL, '0', '0', 105352633, 1, 'RUB', NULL, 'ЛСТ-1262707112-1', '2019-02-20 23:32:37.772052', '2019-02-20 19:10:59.334911', '2019-02-20 20:32:37.700099', 4);
INSERT INTO parks.balances ("ContractID", "Balance", "CurrMonthCharge", "CommissionToPay", "CurrMonthBonus", "BonusLeft", "ClientID", "OfferAccepted", "Currency", "NettingLastDt", "PersonalAccountExternalID", "DT", "created", "updated", "revision") VALUES (1040309, '0', '0', NULL, '0', '0', 105423433, 1, 'RUB', NULL, 'ЛСТ-1262870339-1', '2019-02-20 23:32:37.779176', '2019-02-20 20:32:37.700099', '2019-02-20 20:32:37.700099', 5);

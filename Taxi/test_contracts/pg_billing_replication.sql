INSERT INTO parks.clients (id, park_id, created, updated) VALUES
    ('103917439', '100', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP)),
    ('105352633', '200', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP)),
    ('105391493', '300', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP)),
    ('105423433', '300', CAST('2017-01-01 10:00:00.000001' AS TIMESTAMP), CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP));

ALTER TABLE parks.contract_versions DISABLE TRIGGER parks_contract_versions_ins_tr;

INSERT INTO parks.contract_versions
(
 "ID", client_id, version, type, "EXTERNAL_ID", "PERSON_ID", "IS_ACTIVE", "IS_SIGNED", "IS_SUSPENDED", "CURRENCY", "NETTING", "NETTING_PCT", "LINK_CONTRACT_ID", "SERVICES", "NDS_FOR_RECEIPT",
 "OFFER_ACCEPTED", "NDS", "PAYMENT_TYPE", "PARTNER_COMMISSION_PCT", "PARTNER_COMMISSION_PCT2",
 "IND_BEL_NDS_PERCENT", "END_DT", "FINISH_DT", "DT", created,
 updated, revision, status, "CONTRACT_TYPE", "IND_BEL_NDS", "COUNTRY", "IS_FAXED", "IS_DEACTIVATED", "IS_CANCELLED", "ATTRIBUTES_HISTORY", "FIRM_ID"
)
VALUES
(
    553918, '1', 1, 'GENERAL', '205101/18', 8349867, 1, 1, 0, 'RUR', 1, '100', NULL, '{128,124,125,605,111}', 18,
    1, NULL, 2, NULL, '5', NULL, NULL, NULL, '2018-09-26 00:00:00', '2019-03-05 10:56:24.664433',
    '2019-02-20 20:52:15.307325', 656, 'ACTIVE', 9, NULL, NULL, 1, 0, 0,
    '{"SERVICES": [["2018-09-26 00:00:00", [128,124,125]], ["2018-09-27 00:00:00", [128,124,125, 605, 111]]], "PARTNER_COMMISSION_PCT2": [["2018-09-26 00:00:00", "5"]]}',
    13
),
(
    553919, '1', 1, 'SPENDABLE', 'РАС-115692', 8349869, 1, 1, 0, 'RUR', NULL, NULL, NULL, '{135}', NULL, NULL, 18,
    NULL, NULL, NULL, NULL, NULL, '2019-03-05 10:56:24', '2018-09-26 00:00:00', '2019-03-05 10:56:24.664433',
    '2019-02-20 20:52:15.307325', 657, 'ACTIVE', 10, '80.19', NULL, NULL, NULL, NULL, NULL, NULL
),
(
    553920, '1', 1, 'SPENDABLE', 'spendta-205101/18', 8349869, 1, 1, 0, 'RUR', NULL, NULL, 553918, '{137}', NULL,
    NULL, 18, NULL, NULL, NULL, NULL, '2019-02-20 20:52:15', NULL, '2018-09-26 00:00:00', '2019-03-05 10:56:24.664433',
    '2019-02-20 20:52:15.307325', 658, 'ACTIVE', NULL, '23.44', 225, NULL, NULL, NULL, NULL, NULL
);

INSERT INTO parks.contract_versions(
    "ID",
    client_id,
    version,
    type,
    updated,
    created,
    expired,
    "IS_SIGNED",
    "IS_FAXED",
    "IS_CANCELLED",
    "IS_DEACTIVATED",
    "IS_SUSPENDED",
    "DT",
    "FINISH_DT",
    "END_DT",
    "SERVICES",
    "LINK_CONTRACT_ID",
    "CURRENCY",
    "ATTRIBUTES_HISTORY"
)
VALUES (
    -- base active configuration
    1,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-01-21 09:10:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    '2020-01-21 09:10:00.000000', -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-12-31 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{111}'::int[],               -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'RUB',                        -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- currency changed
    1,                            -- ID
    '103917439',                  -- client_id
    2,                            -- version
    'GENERAL',                    -- type
    '2020-01-21 09:10:00.000000', -- updated
    '2020-01-21 09:10:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-12-31 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{111}'::int[],               -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'USD',                        -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- not active (for active_ts=2020-01-21) due to FINISH_DT
    2,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2019-01-01 00:00:00.000000', -- DT
    '2020-01-21 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{111, 650}'::int[],          -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'USD',                        -- CURRENCY
    '{"SERVICES": [["2019-01-01 00:00:00", [111, 650]]], "PARTNER_COMMISSION_PCT2": []}'  -- ATTRIBUTES_HISTORY
),
(
    -- the same as the previous but active cause +1 day for spendable
    3,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'SPENDABLE',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2019-01-01 00:00:00.000000', -- DT
    NULL,                         -- FINISH_DT
    '2020-01-21 00:00:00.000000', -- END_DT
    '{137}'::int[],               -- SERVICES
    1,                            -- LINK_CONTRACT_ID
    'USD',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- not active due to LINK_CONTRACT_ID
    4,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'SPENDABLE',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    NULL,                         -- FINISH_DT
    '2020-01-21 00:00:00.000000', -- END_DT
    '{137}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'USD',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- active cause LINK_CONTRACT_ID is checking for 137 service only
    5,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'SPENDABLE',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    NULL,                         -- FINISH_DT
    '2020-01-21 00:00:00.000000', -- END_DT
    '{651}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'USD',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- not active cause not IS_SIGNED and not IS_FAXED
    6,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'SPENDABLE',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    0,                            -- IS_SIGNED
    0,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    NULL,                         -- FINISH_DT
    '2020-01-21 00:00:00.000000', -- END_DT
    '{651}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'USD',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- not active cause IS_CANCELLED
    7,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'SPENDABLE',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    1,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    NULL,                         -- FINISH_DT
    '2020-01-21 00:00:00.000000', -- END_DT
    '{651}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'USD',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    8,                            -- ID
    '103917444',                  -- client_id
    1,                            -- version
    'GENERAL',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    1,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-01-21 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{135}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'RUB',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    9,                            -- ID
    '103917444',                  -- client_id
    1,                            -- version
    'GENERAL',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    1,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-01-21 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{668}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'RUB',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    10,                           -- ID
    '105352445',                  -- client_id
    1,                            -- version
    'GENERAL',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    1,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-01-21 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{135}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'RUB',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- general
    11,                           -- ID
    '103917440',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-05-20 22:45:00.000000', -- updated
    '2020-05-20 22:45:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-05-21 00:00:00',        -- DT
    '2020-08-21 00:00:00',        -- FINISH_DT
    NULL,                         -- END_DT
    '{111, 128}'::int[],          -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'RUB',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- spendable, ends before linked general
    12,                           -- ID
    '103917440',                  -- client_id
    1,                            -- version
    'SPENDABLE',                  -- type
    '2020-05-20 22:45:00.000000', -- updated
    '2020-05-20 22:45:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-05-21 00:00:00',        -- DT
    NULL,                         -- FINISH_DT
    '2020-08-18 00:00:00',        -- END_DT
    '{137}'::int[],               -- SERVICES
    11,                           -- LINK_CONTRACT_ID
    'RUB',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    --  newer version of 16
    13,                           -- ID
    '111111111',                  -- client_id
    1,                            -- version
    'GENERAL',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    1,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-12-01 00:00:00.000000', -- DT
    '2020-12-21 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{135}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'RUB',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- general suspended
    14,                           -- ID
    '103917440',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-05-20 22:45:00.000000', -- updated
    '2020-05-20 22:45:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    1,                            -- IS_SUSPENDED
    '2020-12-31 00:00:00',        -- DT
    NULL,                         -- FINISH_DT
    NULL,                         -- END_DT
    '{111, 128}'::int[],          -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'RUB',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- general
    15,                           -- ID
    '103917440',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-05-20 22:45:00.000000', -- updated
    '2020-05-20 22:45:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2021-01-25T00:00:00+0000',   -- DT
    NULL,                         -- FINISH_DT
    NULL,                         -- END_DT
    '{111, 128}'::int[],          -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'RUB',                        -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    16,                           -- ID
    '111111111',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    1,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-01-21 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{135}'::int[],               -- SERVICES
    2,                            -- LINK_CONTRACT_ID
    'RUB',                        -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- not active (for active_ts=2020-01-21) due to FINISH_DT
    17,                            -- ID
    '105352633',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2019-01-01 00:00:00.000000', -- DT
    '2020-01-21 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{111, 650}'::int[],          -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'USD',                        -- CURRENCY
    '{"SERVICES": [["2019-01-01 00:00:00", [111, 650]]], "PARTNER_COMMISSION_PCT2": []}'  -- ATTRIBUTES_HISTORY
),
(
    -- not active due to LINK_CONTRACT_ID
    18,                            -- ID
    '105352633',                  -- client_id
    1,                            -- version
    'SPENDABLE',                  -- type
    '2020-01-21 09:00:00.000000', -- updated
    '2020-01-21 09:00:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    NULL,                         -- FINISH_DT
    '2020-01-21 00:00:00.000000', -- END_DT
    '{1164}'::int[],               -- SERVICES
    17,                            -- LINK_CONTRACT_ID
    'USD',                         -- CURRENCY
    NULL                          -- ATTRIBUTES_HISTORY
)
;

ALTER TABLE parks.contract_versions ENABLE TRIGGER parks_contract_versions_ins_tr;

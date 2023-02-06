ALTER TABLE parks.contract_versions DISABLE TRIGGER parks_contract_versions_ins_tr;

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
    "PARTNER_COMMISSION_PCT2",
    "ATTRIBUTES_HISTORY"
)
VALUES (
    1,                            -- ID
    '000000000',                  -- client_id
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
        '3',                           -- PARTNER_COMMISSION_PCT2
    NULL                          -- ATTRIBUTES_HISTORY
),
       (
    2,                            -- ID
    '000000001',                  -- client_id
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
    '3',                           -- PARTNER_COMMISSION_PCT2
    '{"SERVICES": [["2020-01-01 00:00:00.000000", [111, 124]], ["2020-03-01 00:00:00.000000", [111]]], "PARTNER_COMMISSION_PCT2": []}'  -- ATTRIBUTES_HISTORY
),
              (
    3,                            -- ID
    '000000002',                  -- client_id
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
    '5',                           -- PARTNER_COMMISSION_PCT2
    '{"SERVICES": [["2020-01-01 00:00:00.000000", [111, 124]], ["2020-03-01 00:00:00.000000", [111]]], "PARTNER_COMMISSION_PCT2": [["2020-01-01 00:00:00.000000", "5"], ["2020-04-01 00:00:00.000000", "6"]], "YANDEX_BANK_ENABLED": [["2020-03-01 00:00:00.000000", 0]]}'  -- ATTRIBUTES_HISTORY
);

ALTER TABLE parks.contract_versions ENABLE TRIGGER parks_contract_versions_ins_tr;

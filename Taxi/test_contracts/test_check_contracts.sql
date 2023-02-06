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
    'RUR',                        -- CURRENCY,
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
    'USD',                        -- CURRENCY,
    NULL                          -- ATTRIBUTES_HISTORY
),
(
    -- services from attr history
    2,                            -- ID
    '103917439',                  -- client_id
    1,                            -- version
    'GENERAL',                    -- type
    '2020-01-21 09:11:00.000000', -- updated
    '2020-01-21 09:10:00.000000', -- created
    '2020-01-21 09:11:00.000000', -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-12-31 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{650}'::int[],               -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'USD',                        -- CURRENCY,
    '{"SERVICES": [["2020-01-01 00:00:00", [650]]], "PARTNER_COMMISSION_PCT2": []}' -- ATTRIBUTES_HISTORY
),
(
    -- services from attr history
    2,                            -- ID
    '103917439',                  -- client_id
    2,                            -- version
    'GENERAL',                    -- type
    '2020-01-21 09:11:00.000000', -- updated
    '2020-01-21 09:11:00.000000', -- created
    NULL,                         -- expired
    1,                            -- IS_SIGNED
    1,                            -- IS_FAXED
    0,                            -- IS_CANCELLED
    0,                            -- IS_DEACTIVATED
    0,                            -- IS_SUSPENDED
    '2020-01-01 00:00:00.000000', -- DT
    '2020-12-31 00:00:00.000000', -- FINISH_DT
    NULL,                         -- END_DT
    '{650}'::int[],               -- SERVICES
    NULL,                         -- LINK_CONTRACT_ID
    'USD',                        -- CURRENCY,
    '{"SERVICES": [["2020-01-01 00:00:00", [650]], ["2099-01-01 00:00:00", [650, 672]]]}'  -- ATTRIBUTES_HISTORY
);

ALTER TABLE parks.contract_versions ENABLE TRIGGER parks_contract_versions_ins_tr;

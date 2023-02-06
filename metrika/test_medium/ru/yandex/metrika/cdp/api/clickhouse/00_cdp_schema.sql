CREATE TABLE IF NOT EXISTS default.cdp_clients
(
    `CounterID` UInt32,
    `CDPUID` UInt64,
    `ClientVersion` UInt32,
    `UserIDs` Array(UInt64),
    `ClientIDs` Array(UInt64),
    `CryptaIDs` Array(UInt64),
    `GluedYuids` Array(UInt64),
    `CreateTime` DateTime,
    `UpdateTime` DateTime,
    `ExternalHardID` String,
    `ClientType` Enum8('CONTACT' = 1, 'COMPANY' = 2),
    `Status` Enum8('ACTIVE' = 1, 'DELETED' = 2),
    `ParentCDPUID` UInt64,
    `Name` String,
    `BirthDate` Date,
    `Emails` Array(String),
    `Phones` Array(String),
    `Attributes.Key` Array(String),
    `Attributes.Value` Array(String),
    `ClientUserIDs` Array(String),
    `OrdersSum` UInt64,
    `LTV` Int64,
    `FirstOrderCreateTime` DateTime,
    `LastOrderCreateTime` DateTime,
    `CompletedOrders` UInt32,
    `CreatedOrders` UInt32,
    `PaidOrders` UInt32,
    `PartitionID` UInt8,
    `EmailsMd5` Array(String),
    `PhonesMd5` Array(String)
)
ENGINE = ReplacingMergeTree(ClientVersion)
PARTITION BY PartitionID
ORDER BY (CounterID, CDPUID)
SETTINGS index_granularity = 8192;

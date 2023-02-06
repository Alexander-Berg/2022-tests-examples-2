CREATE DATABASE IF NOT EXISTS cdp;

CREATE TABLE cdp.orders_d
(
    `CounterID`         UInt32,
    `CreateTime`        DateTime,
    `CDPUID`            UInt64,
    `OrderID`           UInt64,
    `OrderVersion`      UInt32,
    `Status`            Enum8('ACTIVE' = 1, 'DELETED' = 2),
    `UpdateTime`        DateTime,
    `FinishTime`        DateTime,
    `Revenue`           UInt64,
    `Cost`              UInt64,
    `OrderStatus`       String,
    `Products.ID`       Array(String),
    `Products.Quantity` Array(UInt32),
    `Attributes.Key`    Array(String),
    `Attributes.Value`  Array(String),
    `PartitionID`       UInt8,
    `ExternalOrderID`   String,
    `LastUploadings`    Array(String),
    `SystemLastUpdate`  DateTime
) ENGINE = ReplacingMergeTree(OrderVersion)
PARTITION BY PartitionID
ORDER BY (CounterID, CreateTime, CDPUID, OrderID)
SAMPLE BY CDPUID
SETTINGS index_granularity = 8192;

CREATE DATABASE mtmobproxy;

CREATE TABLE mtmobproxy.logs_weekly
(
    `ServerName` String,
    `DC` FixedString(3),
    `RequestDate` Date,
    `RequestDateTime` DateTime,
    `ClientIP6` FixedString(16),
    `VirtualHost` String,
    `Path` String,
    `BasePath` String DEFAULT 'misc',
    `Params.Keys` Array(String),
    `Params.Values` Array(String),
    `Code` UInt16,
    `RequestLengthBytes` UInt32,
    `FullRequestTime` UInt16,
    `UpstreamResponseTime` UInt16,
    `IsUpstreamRequest` Enum8('false' = 0, 'true' = 1),
    `SSLHanshakeTime` UInt16,
    `IsKeepalive` Enum8('false' = 0, 'true' = 1),
    `StringHash` UInt32,
    `HTTPMethod` String
)
ENGINE = MergeTree()
PARTITION BY toMonday(RequestDate)
ORDER BY (BasePath, Code, ServerName, StringHash)
SAMPLE BY StringHash
SETTINGS index_granularity = 8192;

CREATE DATABASE qloud;

CREATE TABLE qloud.logs_weekly
(
    `RequestDate` Date DEFAULT toDate(RequestDateTime),
    `RequestDateTime` DateTime,
    `ClientIP6` FixedString(16) DEFAULT IPv6StringToNum(ClientIP6String),
    `ClientIP6String` String,
    `VirtualHost` String,
    `Path` String,
    `BasePath` String DEFAULT 'misc',
    `Params.Keys` Array(String),
    `Params.Values` Array(String),
    `Code` UInt16,
    `FullRequestTime` UInt16,
    `UpstreamResponseTime` UInt16,
    `Container` String
)
ENGINE = MergeTree()
PARTITION BY toMonday(RequestDate)
ORDER BY (VirtualHost, BasePath, Code, Container)
SETTINGS index_granularity = 8192;

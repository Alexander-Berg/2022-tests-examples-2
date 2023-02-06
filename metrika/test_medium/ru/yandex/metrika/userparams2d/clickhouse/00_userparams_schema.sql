CREATE
DATABASE user_param;

CREATE TABLE user_param.user_param
(
    `UpdateTime`  DateTime,
    `CounterID`   UInt32,
    `UserID`      UInt64,
    `FullPath`    String,
    `Key1`        String,
    `Key2`        String,
    `Key3`        String,
    `Key4`        String,
    `Key5`        String,
    `Key6`        String,
    `Key7`        String,
    `Key8`        String,
    `Key9`        String,
    `Key10`       String,
    `ValueString` String,
    `ValueDouble` Float64,
    `Version`     UInt64,
    `Deleted`     UInt8,
    `ShardID`     UInt32,
    `_timestamp`  DateTime,
    `_partition`  String,
    `_offset`     UInt64,
    `_idx`        UInt32,
    `_rest`       Nullable(String)
) ENGINE = ReplacingMergeTree(Version)
ORDER BY (CounterID, FullPath, intHash32(UserID), UserID)
SAMPLE BY intHash32(UserID)
SETTINGS index_granularity = 8192

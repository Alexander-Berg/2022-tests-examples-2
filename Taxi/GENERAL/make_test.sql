create TABLE internal_trackstory.test$storage
       ON CLUSTER '{cluster}'
(
    pipeline String,
    contractor_dbid String,
    contractor_uuid String,
    unix_timestamp DateTime64(6, 'UTC'),
    backend_recieve_unix_timestamp DateTime64(6, 'UTC'),
    source String,
    lon Float64,
    lat Float64,
    direction Nullable(Float64),
    speed Nullable(Float64),
    altitude Nullable(Float64),
    accuracy Nullable(Float64),
    iso_eventtime String EPHEMERAL '',
    `timestamp` DateTime EPHEMERAL 0,
    _rest String EPHEMERAL '',
    _delivery__rest String EPHEMERAL '',
    _logfeller_timestamp UInt64 EPHEMERAL 0,
    _timestamp DateTime EPHEMERAL 0,
    _partition String EPHEMERAL '',
    _offset UInt64 EPHEMERAL 0,
    _idx UInt32 EPHEMERAL 0
)
ENGINE = ReplicatedMergeTree
ORDER BY (contractor_uuid, contractor_dbid, unix_timestamp)
TTL toDateTime(backend_recieve_unix_timestamp) + INTERVAL 2 DAY DELETE,
    toDateTime(backend_recieve_unix_timestamp) + INTERVAL 24 HOUR TO DISK 'object_storage'
SETTINGS ttl_only_drop_parts=1;


CREATE TABLE internal_trackstory.test
      ON CLUSTER '{cluster}' AS internal_trackstory.test$storage
ENGINE = Distributed(
    '{cluster}',
    internal_trackstory, test$storage,
    cityHash64(contractor_uuid));

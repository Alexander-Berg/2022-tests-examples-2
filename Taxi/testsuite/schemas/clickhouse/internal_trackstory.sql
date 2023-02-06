CREATE TABLE internal_trackstory.test (
    pipeline String ,
    contractor_dbid String ,
    contractor_uuid String ,
    source String ,
    unix_timestamp DateTime64(6, 'UTC') ,
    lon Float64 ,
    lat Float64 ,
    altitude Nullable(Float64),
    direction Nullable(Float64),
    speed Nullable(Float64),
    accuracy Nullable(Float64),
    backend_recieve_unix_timestamp DateTime64(6, 'UTC')
) ENGINE=MergeTree()
  PRIMARY KEY contractor_uuid;

UPSERT INTO `parsed-internal-position-log-2/taxi` 
(unix_timestamp, contractor_uuid, contractor_dbid, lat, lon, backend_recieve_unix_timestamp) VALUES
(CAST(1568196015000000 AS TIMESTAMP), "uuid_7", "dbid", 37.0, 55.0, CAST(1568196015000000 AS TIMESTAMP));

UPSERT INTO `parsed-internal-position-log-2/test` 
(unix_timestamp, contractor_uuid, contractor_dbid, lat, lon, backend_recieve_unix_timestamp) VALUES
(CAST(1568196015000000 AS TIMESTAMP), "uuid_7", "dbid", 37.0, 55.0, CAST(1568196015000000 AS TIMESTAMP));

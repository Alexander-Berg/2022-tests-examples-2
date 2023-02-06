UPSERT INTO `parsed-internal-position-log-2/taxi` 
(unix_timestamp, contractor_uuid, contractor_dbid, lat, lon, speed, direction) VALUES
(CAST(1568196015000000 AS TIMESTAMP), "uuid_7", "dbid", 37.0, 55.0, 32.0, 336),
(CAST(1568196015000000 AS TIMESTAMP), "uuid_8", "dbid", 37.5, 55.5, 32.0, 336),
(CAST(1568196015000000 AS TIMESTAMP), "uuid_7", "dbid_2", 37.4, 55.4, 32.0, 336),
(CAST(1568197400000000 AS TIMESTAMP), "uuid_7", "dbid", 38.0, 56.0, 33.0, 337),
(CAST(1568192414000000 AS TIMESTAMP), "uuid_7", "dbid", 36.0, 54.0, 34.0, 338)

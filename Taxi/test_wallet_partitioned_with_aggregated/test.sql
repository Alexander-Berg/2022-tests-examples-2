INSERT INTO common.udids (udid_id,udid,master_udid_id)VALUES
(1001,'000000000000000000000001',NULL);

CREATE TEMPORARY SEQUENCE event_id_for_data_logs START WITH 10001;
WITH series AS (
	SELECT
		nextval('event_id_for_data_logs') as event_id,
		generate_series(
			'2021-12-22 10:00:03'::timestamp AT TIME ZONE 'UTC',
			'2021-12-22 10:00:03'::timestamp AT TIME ZONE 'UTC' + '40 days'::interval,
			'9 minutes'
		) as created
)
INSERT INTO data.logs_64_partitioned
	(event_id, udid_id, created, loyalty_increment, activity_increment)
SELECT
	event_id,
	1001 as udid_id,
	created,
	(event_id % 10) as loyalty_increment,
       	0 as activity_increment
FROM series;

DROP SEQUENCE event_id_for_data_logs;

INSERT INTO common.range_partitions_metadata (
	origin_table_schema, origin_table_name, 
	table_schema, table_name, 
	range_since, range_until,
	filling_since,
	state
)
VALUES
  (
	'data', 'logs_64_loyalty_daily_aggregated',
	'data', 'logs_64_loyalty_daily_aggregated_20211223000000_20211224000000',
	'2021-12-23 00:00:00', '2021-12-24 00:00:00', 
	'2021-12-24 00:00:00',
	'ready'::PartitionState
  ),
  (
	'data', 'logs_64_loyalty_daily_aggregated',
	'data', 'logs_64_loyalty_daily_aggregated_20211224000000_20211225000000',
	'2021-12-24 00:00:00', '2021-12-25 00:00:00', 
	'2021-12-25 00:00:00',
	'ready'::PartitionState
  );

CREATE TABLE data.logs_64_loyalty_daily_aggregated_20211223000000_20211224000000
    (LIKE data.logs_64_loyalty_daily_aggregated);
CREATE UNIQUE INDEX
  unique_idx_udid_id_20211223000000_20211224000000
  ON data.logs_64_loyalty_daily_aggregated_20211223000000_20211224000000 (udid_id);
ALTER TABLE data.logs_64_loyalty_daily_aggregated_20211223000000_20211224000000
  ADD CONSTRAINT range_20211223000000_20211224000000
  CHECK('2021-12-23 00:00:00' <= since AND until < '2021-12-24 00:00:00');
WITH aggregated_data as (
          SELECT
               udid_id,
               SUM(loyalty_increment) as loyalty_summary,
               COUNT(*) as records_count,
               MIN(created) as since,
               MAX(created) as until
          FROM data.logs_64_partitioned
          WHERE '2021-12-23 00:00:00' <= created
	    AND created < '2021-12-24 00:00:00'
          GROUP BY udid_id
)
INSERT INTO data.logs_64_loyalty_daily_aggregated_20211223000000_20211224000000
SELECT * FROM aggregated_data;
UPDATE data.logs_64_loyalty_daily_aggregated_20211223000000_20211224000000
  SET loyalty_summary = loyalty_summary + 1;
ALTER TABLE data.logs_64_loyalty_daily_aggregated
  ATTACH PARTITION data.logs_64_loyalty_daily_aggregated_20211223000000_20211224000000
  FOR VALUES FROM ('2021-12-23 00:00:00') TO ('2021-12-24 00:00:00');

CREATE TABLE data.logs_64_loyalty_daily_aggregated_20211224000000_20211225000000
    (LIKE data.logs_64_loyalty_daily_aggregated);
CREATE UNIQUE INDEX
  unique_idx_udid_id_20211224000000_20211225000000
  ON data.logs_64_loyalty_daily_aggregated_20211224000000_20211225000000 (udid_id);
ALTER TABLE data.logs_64_loyalty_daily_aggregated_20211224000000_20211225000000
  ADD CONSTRAINT range_20211224000000_20211225000000
  CHECK('2021-12-24 00:00:00' <= since AND until < '2021-12-25 00:00:00');
WITH aggregated_data as (
          SELECT
               udid_id,
               SUM(loyalty_increment) as loyalty_summary,
               COUNT(*) as records_count,
               MIN(created) as since,
               MAX(created) as until
          FROM data.logs_64_partitioned
          WHERE '2021-12-24 00:00:00' <= created
	    AND created < '2021-12-25 00:00:00'
          GROUP BY udid_id
)
INSERT INTO data.logs_64_loyalty_daily_aggregated_20211224000000_20211225000000
SELECT * FROM aggregated_data;
UPDATE data.logs_64_loyalty_daily_aggregated_20211224000000_20211225000000
  SET loyalty_summary = loyalty_summary + 2;
ALTER TABLE data.logs_64_loyalty_daily_aggregated
  ATTACH PARTITION data.logs_64_loyalty_daily_aggregated_20211224000000_20211225000000
  FOR VALUES FROM ('2021-12-24 00:00:00') TO ('2021-12-25 00:00:00');

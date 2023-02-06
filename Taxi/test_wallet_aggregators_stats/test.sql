INSERT INTO common.udids (udid_id,udid,master_udid_id)VALUES
(1001,'000000000000000000000001',NULL),
(1002,'000000000000000000000002',NULL);

CREATE TEMPORARY SEQUENCE event_id_for_data_logs START WITH 10001;
WITH series AS (
	SELECT
		nextval('event_id_for_data_logs') as event_id,
		generate_series(
			'2021-12-22 10:00:03'::timestamp AT TIME ZONE 'UTC',
			'2021-12-22 10:00:03'::timestamp AT TIME ZONE 'UTC' + '3 days'::interval,
			'9 minutes'
		) as created
)
INSERT INTO data.logs_64_partitioned
	(event_id, udid_id, created, loyalty_increment, activity_increment)
SELECT
	event_id,
	1001 + event_id % 2 as udid_id,
	created,
	(event_id % 10) as loyalty_increment,
       	0 as activity_increment
FROM series;

DROP SEQUENCE event_id_for_data_logs;


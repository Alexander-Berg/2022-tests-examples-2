DELETE FROM eats_report_storage.place_plus_metric
WHERE _etl_processed_at < '2021-08-10 12:17'::timestamp OR utc_period_start_dttm < '2021-07-01 00:00+00:00'::timestamptz;

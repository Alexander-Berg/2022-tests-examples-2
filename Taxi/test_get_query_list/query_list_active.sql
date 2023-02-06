INSERT INTO gp.res_group_status (database_name, res_group_id, res_group_name, concurrency, cpu_utilization, cpu_utilization_percent, vmem_utilization, vmem_utilization_percent, vmem_fixed, vmem_fixed_percent, update_dttm) VALUES ('butthead', 6437, 'default_group', 50, 0, 0.04, 0, 0, 1152, 0.11, '2022-07-26 18:31:08.600163');
INSERT INTO gp.res_group_status (database_name, res_group_id, res_group_name, concurrency, cpu_utilization, cpu_utilization_percent, vmem_utilization, vmem_utilization_percent, vmem_fixed, vmem_fixed_percent, update_dttm) VALUES ('butthead', 6438, 'admin_group', 60, 1, 0.35, 0, 0, 3600, 0.8, '2022-07-26 18:31:08.600163');
INSERT INTO gp.res_group_status (database_name, res_group_id, res_group_name, concurrency, cpu_utilization, cpu_utilization_percent, vmem_utilization, vmem_utilization_percent, vmem_fixed, vmem_fixed_percent, update_dttm) VALUES ('ritchie', 16392, 'etl_group', 90, 1194, 169.61, 262912, 2.92, 3620528, 40.18, '2022-07-26 18:31:09.016596');
INSERT INTO gp.res_group_status (database_name, res_group_id, res_group_name, concurrency, cpu_utilization, cpu_utilization_percent, vmem_utilization, vmem_utilization_percent, vmem_fixed, vmem_fixed_percent, update_dttm) VALUES ('ritchie', 6438, 'admin_group', 50, 193, 27.42, 353456, 12.16, 896400, 30.85, '2022-07-26 18:31:09.016596');

INSERT INTO gp.query_vmem_size (database_name, sess_id, vmem_size_gb, update_dttm) VALUES ('butthead', 912356,    1.5, '2022-07-26 18:33:08.833468');
INSERT INTO gp.query_vmem_size (database_name, sess_id, vmem_size_gb, update_dttm) VALUES ('butthead', 911396,    1.5, '2022-07-26 18:33:08.833468');
INSERT INTO gp.query_vmem_size (database_name, sess_id, vmem_size_gb, update_dttm) VALUES ('ritchie', 111025,    2.03, '2022-07-26 18:33:08.833468');
INSERT INTO gp.query_vmem_size (database_name, sess_id, vmem_size_gb, update_dttm) VALUES ('ritchie', 111741,    4.06, '2022-07-26 18:33:08.833468');

INSERT INTO gp.query_activity (database_name, pid, sess_id, res_group_id, user_name, query, query_start, query_waiting,
                               update_dttm)
VALUES ( 'butthead', 576332, 912356, 6438, 'robot-taxi-tst-gpadm', '
    SELECT prg.oid                                                                                  AS resgroupid
       , rgs.rsgname
       , prc1.value::INT AS concurrency
       , round(rgs.cpu, 0) AS cpu_used
       , round((rgs.cpu::NUMERIC / (rgs.host_count * 56 * (prc2.value::NUMERIC / 100))) * 100, 2) AS cpu_used_prc
       , round((rgs.memory_used::NUMERIC / rgs.memory_available::NUMERIC) * 100, 2) AS vmem_used_prc
       , round((rgs.memory_fixed::NUMERIC / rgs.memory_available::NUMERIC) * 100, 2) AS vmem_fixed_prc
       , round(rgs.memory_used, 2) AS memory_used
       , round(rgs.memory_fixed, 2) AS memory_fixed
        FROM (SELECT rsgname
           ', '2022-07-26 18:19:35.000000', false, '2022-07-26 18:19:35.142024');
INSERT INTO gp.query_activity (database_name, pid, sess_id, res_group_id, user_name, query, query_start, query_waiting,
                               update_dttm)
VALUES ('butthead', 548091, 911396, 6437, 'vasilevel', 'with saved_age as (select greatest(coalesce(nullif(greatest(pg_catalog.age(pg_catalog.xidin(pg_catalog.int8out($1))), -1), -1), 2147483647), coalesce(nullif(greatest(pg_catalog.age(pg_catalog.xidin(pg_catalog.int8out($2))), -1), -1), 2147483647)) as "value")
select pg_catalog.age(C.last_tx) <= (case when SA."value" < 0 then 2147483647 else SA."value" end) as has_changes from
(
  select X.last_tx as last_tx
  from (
    (
    select xmin as last_tx
      from pg_catalog.pg_type
      where typnamespace = $3::oid
      order by pg_catalog.age(xmin)
      limit 1
    )
    union all
    (
    select E.xmin as last_tx
      from pg_catalog.pg_exttable E
        join pg_catalog.pg_class C on E.reloid = C.oid
      where C.relnamespace = $4::oid
      order by pg_catalog.age(E.xmin)
      limit 1
    )
    union all
    (
    select xmin as last_tx
      from pg_catalog.pg_class
      where relnamespace = $5::oid
      order by pg_catalog.age(xmin)
      limit 1
    )
    union all
    (
    select xmin as last_tx', '2022-07-26 18:19:33.000000', false, '2022-07-26 18:19:35.142024');
INSERT INTO gp.query_activity (database_name, pid, sess_id, res_group_id, user_name, query, query_start, query_waiting, update_dttm) VALUES ('ritchie', 355836, 111025, 6438, 'robot-taxi-gpadmin', '
        ANALYZE "rep"."amr_dm_amr_geo_tariff_1_prt_daily_2_prt_2021";
    ', '2022-07-26 18:19:11.000000', false, '2022-07-26 18:19:35.944444');
INSERT INTO gp.query_activity (database_name, pid, sess_id, res_group_id, user_name, query, query_start, query_waiting, update_dttm) VALUES ('ritchie', 360705, 111741, 16392, 'etl', 'SELECT * FROM ctl.loader_period_snapshot(''stg.taxi_ods_blocklist_event_log_5677b049df'',''taxi_ods_blocklist.event_log'',''utc_event_dttm'',''2022-07-23 00:00:00.000000'',''2022-07-24 23:59:59.999999'')', '2022-07-26 18:18:14.000000', false, '2022-07-26 18:19:35.944444');

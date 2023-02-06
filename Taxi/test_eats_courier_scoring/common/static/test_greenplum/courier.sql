INSERT INTO eda_ods_bigfood.region (
    id, name
) VALUES (
    777, 'Москва'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO taxi_ods_dbdrivers.executor_profile (
    executor_profile_id, park_taximeter_id, driver_license_pd_id, bigfood_courier_id, work_status_code
) VALUES
      ('courier_uuid1', 'courier_dbid1', 'license_id1', 1, 'working'),
      ('courier_uuid2', 'courier_dbid2', 'license_id2', 2, 'working')
ON CONFLICT (executor_profile_id, park_taximeter_id) DO NOTHING;

INSERT INTO eda_ods_bigfood.courier_meta_data (
    courier_id, rover_flg
) VALUES (1, false), (2, false) ON CONFLICT (courier_id) DO NOTHING;

INSERT INTO eda_cdm_marketplace.dm_order (
    courier_id, order_id, order_status, local_created_dttm, utc_created_dttm, flow_type, order_delivery_type, brand_store_flg, taxi_dispatch_reason_code, courier_username
) VALUES (
    1, 100, 4, '2020-09-19 08:00:00', '2020-09-19 05:00:00', 'eda', 'native', false, 'redirected_by_supply', 'Username Courier'
), (
    2, 200, 4, '2020-09-19 08:00:00', '2020-09-19 05:00:00', 'eda', 'native', false, 'redirected_by_supply', 'Username Courier 2 '
), (
    2, 300, 4, '2020-09-23 08:00:00', '2020-09-23 05:00:00', 'eda', 'native', false, 'redirected_by_supply', 'Username Courier 2'
), (
    2, 400, 4, '2020-09-23 10:00:00', '2020-09-23 07:00:00', 'eda', 'native', false, 'redirected_by_supply', 'Username Courier 2'
), (
    2, 500, 4, '2020-09-23 12:00:00', '2020-09-23 09:00:00', 'eda', 'native', false, 'redirected_by_supply', 'Username Courier 2'
), (
    2, 600, 4, '2020-09-26 10:00:00', '2020-09-26 07:00:00', 'eda', 'native', false, 'redirected_by_supply', 'Username Courier 2'
)  ON CONFLICT (order_id) DO NOTHING;

INSERT INTO eda_ods_bigfood.courier (
    id, pool_name, work_status, region_id, username, type
) VALUES (
    1, 'eda', 'working', 777, 'Username Courier 1', 'courier_type'
), (
    2, 'eda', 'working', 777, 'Username Courier 2', 'courier_type'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO eda_ods_bigfood.courier_deactivation_reason (
    reason_id, alias_code
) values (1, 'oko'), (2, 'other'), (3, 'another') ON CONFLICT (reason_id) DO NOTHING;

INSERT INTO eda_ods_bigfood.courier_deactivation_info (
    courier_deactivation_id, courier_deactivation_reason_id, courier_id, deactivation_reason_comment, utc_created_dttm, utc_updated_dttm
) VALUES
 (1, 1, 2, 'oko deactivation', '2020-09-18 06:00:00', '2020-09-20 06:00:00'),
 (2, 1, 2, 'oko deactivation 2', '2020-09-22 06:00:00', '2020-09-22 06:00:00'),
 (3, 2, 2, 'oko deactivation 2', '2020-09-22 06:00:00', '2020-09-23 07:00:00'),
 (4, 3, 2, 'other deactivation 2', '2020-09-24 06:00:00', '2020-09-24 07:00:00')
 ON CONFLICT (courier_deactivation_id) DO NOTHING;

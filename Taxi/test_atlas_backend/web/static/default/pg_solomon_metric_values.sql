INSERT INTO taxi_db_postgres_atlas_backend.source (
    source_cluster,
    source_type,
    source_path,
    source_name,
    description,
    is_partitioned,
    partition_key,
    partition_template,
    author,
    created_at,
    changed_by,
    changed_at,
    data_updated_at
) VALUES
(  -- source_id = 1
    'atlastest_mdb',
    'clickhouse',
    'atlas.ods_order',
    'ch_ods_order',
    '',
    False,
    '',
    '',
    '@source_author',
    to_timestamp(1355314332)::timestamp,  -- 2012-12-12 12:12:12+00:00
    '@source_author',
    to_timestamp(1638483742)::timestamp,  -- 2021-12-02 22:22:22+00:00
    to_timestamp(946684800)::timestamp  -- 2000-01-01 00:00:00+00:00
);

INSERT INTO taxi_db_postgres_atlas_backend.source_column (
    source_id,
    column_name,
    description,
    db_type,
    native_type,
    expression,
    metadata,
    is_valid
) VALUES
    (1, 'agent_id', '', 'LowCardinality(Nullable(String))', 'NULLABLE_STR', '', '{}', true),
    (1, 'agent_order_id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'agent_user_type', '', 'LowCardinality(Nullable(String))', 'NULLABLE_STR', '', '{}', true),
    (1, 'application', '', 'String', 'STR', '', '{}', true),
    (1, 'assigned_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'calc_alternative_type', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cancel_wasted_time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'cancelled_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'cand_cnt', '', 'String', 'STR', '', '{}', true),
    (1, 'cand_first_adjusted_point__geopoint', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'cand_first_cp__dest_quadkey', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_first_cp__id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_first_cp__left_dist', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'cand_first_cp__left_time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'cand_first_dist', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_first_dp', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'cand_first_driver_classes', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'cand_first_driver_eta', '', 'DateTime', 'DATETIME', '', '{}', true),
    (1, 'cand_first_driver_points', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_first_gprs_time', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_first_line_dist', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_first_point', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'cand_first_push_on_driver_arriving_send_at_eta', '', 'Nullable(Int32)', 'NULLABLE_INT', '', '{}', true),
    (1, 'cand_first_push_on_driver_arriving_sent', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_first_reposition_mode', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_first_subvention_geoareas', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'cand_first_tags', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'cand_first_taximeter_version', '', 'LowCardinality(String)', 'STR', '', '{}', true),
    (1, 'cand_first_time', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_perf_adjusted_point__geopoint', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'cand_perf_cp__dest_quadkey', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_perf_cp__id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_perf_cp__left_dist', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'cand_perf_cp__left_time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'cand_perf_dist', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_perf_dp', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'cand_perf_driver_classes', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'cand_perf_driver_eta', '', 'DateTime', 'DATETIME', '', '{}', true),
    (1, 'cand_perf_driver_points', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_perf_gprs_time', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_perf_line_dist', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'cand_perf_point', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'cand_perf_push_on_driver_arriving_send_at_eta', '', 'Nullable(Int32)', 'NULLABLE_INT', '', '{}', true),
    (1, 'cand_perf_push_on_driver_arriving_sent', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_perf_reposition_mode', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cand_perf_subvention_geoareas', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'cand_perf_tags', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'cand_perf_taximeter_version', '', 'LowCardinality(String)', 'STR', '', '{}', true),
    (1, 'cand_perf_time', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'car_class', '', 'String', 'STR', '', '{}', true),
    (1, 'car_class_refined', '', 'String', 'STR', '', '{}', true),
    (1, 'cargo_ref_id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'city', '', 'String', 'STR', '', '{}', true),
    (1, 'corp_client_id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'corp_contract_id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'corp_user_id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'cost', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'created', '', 'DateTime', 'DATETIME', '', '{}', true),
    (1, 'dest_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'dest_geopoint', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'dest_quadkey', '', 'String', 'STR', '', '{}', true),
    (1, 'discount_discard_surge', '', 'Nullable(UInt8)', 'NULLABLE_INT', '', '{}', true),
    (1, 'discount_driver_less_coeff', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'discount_method', '', 'String', 'STR', '', '{}', true),
    (1, 'discount_price', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'discount_reason', '', 'String', 'STR', '', '{}', true),
    (1, 'discount_value', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'dispatch_check_in__check_in_time', '', 'Nullable(DateTime)', 'NULLABLE_DATETIME', '', '{}', true),
    (1, 'dispatch_check_in__pickup_line', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'driver_clid', '', 'String', 'STR', '', '{}', true),
    (1, 'driver_dbid', '', 'String', 'STR', '', '{}', true),
    (1, 'driver_id', '', 'String', 'STR', '', '{}', true),
    (1, 'driver_license', '', 'String', 'STR', '', '{}', true),
    (1, 'driver_uuid', '', 'String', 'STR', '', '{}', true),
    (1, 'driving_time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'dttm_utc_1_min', '', 'DateTime', 'DATETIME', '', '{}', true),
    (1, 'failed_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'fastest_class_flg', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'fixed_price__destination', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'fixed_price__destination_quadkey', '', 'String', 'STR', '', '{}', true),
    (1, 'fixed_price__driver_price', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'fixed_price__price', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'fixed_price__price_original', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'fixed_price__show_price_in_taximeter', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'multiorder_order_number', '', 'Nullable(Int32)', 'NULLABLE_INT', '', '{}', true),
    (1, 'nearest_zone', '', 'String', 'STR', '', '{}', true),
    (1, 'no_cars_order', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'offer_timeout_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'order_due', '', 'DateTime', 'DATETIME', '', '{}', true),
    (1, 'order_id', '', 'String', 'STR', '', '{}', true),
    (1, 'order_source', '', 'String', 'STR', '', '{}', true),
    (1, 'order_type', '', 'String', 'STR', '', '{}', true),
    (1, 'overdraft_flg', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'paid_supply', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'paid_supply_price', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'payment_method_id', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'payment_type', '', 'String', 'STR', '', '{}', true),
    (1, 'plan_cost__alternative_type', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'plan_cost__by_tariffs_names', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'plan_cost__by_tariffs_values', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'plan_cost__distance', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'plan_cost__extra_distance_multiplier', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'plan_cost__recalculated', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'plan_cost__time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'preorder_flg', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'price_modifiers__pay_subventions', '', 'Nullable(UInt8)', 'NULLABLE_INT', '', '{}', true),
    (1, 'price_modifiers__reason', '', 'String', 'STR', '', '{}', true),
    (1, 'price_modifiers__tariff_categories', '', 'Array(String)', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'price_modifiers__type', '', 'String', 'STR', '', '{}', true),
    (1, 'price_modifiers__value', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'reorder_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'request_classes', '', 'Array(String)', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'requirements', '', 'Array(String)', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'search_time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'seen_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'seen_timeout_cnt', '', 'Int32', 'INT', '', '{}', true),
    (1, 'source_geoareas', '', 'Array(String)', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'source_geopoint', '', 'Array(Float32)', 'ARRAY_OF_FLOAT', '', '{}', true),
    (1, 'source_metrica_action', '', 'Nullable(String)', 'NULLABLE_STR', '', '{}', true),
    (1, 'source_quadkey', '', 'String', 'STR', '', '{}', true),
    (1, 'status', '', 'String', 'STR', '', '{}', true),
    (1, 'status_updated', '', 'DateTime', 'DATETIME', '', '{}', true),
    (1, 'surcharge', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'surge_alpha', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'surge_beta', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'surge_value', '', 'Float32', 'FLOAT', '', '{}', true),
    (1, 'taxi_status', '', 'String', 'STR', '', '{}', true),
    (1, 'transporting_time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (1, 'ts_1_min', '', 'Int64', 'INT', '', '{}', true),
    (1, 'updated', '', 'DateTime', 'DATETIME', '', '{}', true),
    (1, 'user_agent', '', 'String', 'STR', '', '{}', true),
    (1, 'user_fraud', '', 'UInt8', 'INT', '', '{}', true),
    (1, 'user_id', '', 'String', 'STR', '', '{}', true),
    (1, 'user_tags', '', 'Array(LowCardinality(String))', 'ARRAY_OF_STR', '', '{}', true),
    (1, 'waiting_time', '', 'Nullable(Float32)', 'NULLABLE_FLOAT', '', '{}', true),
    (
        1,
        'counter',
        '',
        'UInt8',
        'INT',
        '1',
        '{}',
        true
    ),
    (
        1,
        'corp_type',
        '',
        'String',
        'STR',
        'CASE WHEN {corp_contract_id} in ( ''544807/20'', ''554742/20'', ''761898/20'' ) THEN ''food'' WHEN {corp_client_id} is not null THEN ''corp'' WHEN {payment_method_id} LIKE ''business%'' THEN ''corp'' ELSE ''not_corp'' END',
        '{}',
        true
    ),
    (
        1,
        'time',
        '',
        'UInt32',
        'INT',
        'toUInt32({dttm_utc_1_min})',
        '{}',
        true
    )
;

INSERT INTO taxi_db_postgres_atlas_backend.dimension (
    dimension_name,
    description,
    dimension_type
) VALUES
    (  -- dimension_id = 1
        'city',
        'Город',
        'STR'
    ),
    (  -- dimension_id = 2
        'tariff',
        'Тариф заказа',
        'STR'
    ),
    (  -- dimension_id = 3
        'corp_type',
        'Тип корпоративного заказа',
        'STR'
    ),
    (  -- dimension_id = 4
        'counter',
        'Счетчик',
        'INT'
    ),
    (  -- dimension_id = 5
        'time',
        'Время',
        'INT'
    )
;

INSERT INTO taxi_db_postgres_atlas_backend.column_dimension_rel (
    source_id,
    column_name,
    dimension_id
) VALUES
    (1, 'city', 1),
    (1, 'car_class', 2),
    (1, 'corp_type', 3),
    (1, 'counter', 4),
    (1, 'time', 5)
;

INSERT INTO taxi_db_postgres_atlas_backend.metric_group (
    ru_name,
    en_name,
    ru_description,
    en_description
) VALUES
    (  -- group_id = 1
        'Метрики',
        'Metrics',
        '',
        ''
    )
;

INSERT INTO taxi_db_postgres_atlas_backend.metric (
    ru_name,
    en_name,
    ru_description,
    en_description,
    group_id
) VALUES
(  -- metric_id = 1
    'Метрика',
    'Metric',
    '',
    '',
    1
)
;

INSERT INTO taxi_db_postgres_atlas_backend.metric_instance (
    metric_id,
    source_id,
    expression,
    use_final,
    filters
) VALUES
(
    1,
    1,
    'SUM({counter})',
    true,
    ARRAY['{city} IN (''Москва'', ''Екатеринбург'', ''Санкт-Петербург'')']
)
;

INSERT INTO taxi_db_postgres_atlas_backend.default_time_dimension (
    metric_id, source_id, dimension_id
) VALUES
    (1, 1, 5)
;

INSERT INTO taxi_db_postgres_atlas_backend.solomon_metric_delivery_settings (
    metric_id,
    source_id,
    duration,
    grid
) VALUES
(  -- delivery_id = 1
    1,
    1,
    300,  -- 5m
    60  -- 1m
)
;

INSERT INTO taxi_db_postgres_atlas_backend.solomon_metric_dimension (
    delivery_id, source_id, dimension_id
) VALUES
    (1, 1, 1),
    (1, 1, 2),
    (1, 1, 3)
;

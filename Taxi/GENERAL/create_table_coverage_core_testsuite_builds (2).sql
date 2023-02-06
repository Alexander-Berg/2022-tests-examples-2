CREATE TABLE coverage_core_testsuite_builds (
    build_id String,
    start_date UInt64,
    coverage_ratio Double,
    endpoints_usage_stat_len Uint64,
    PRIMARY KEY (build_id)
);
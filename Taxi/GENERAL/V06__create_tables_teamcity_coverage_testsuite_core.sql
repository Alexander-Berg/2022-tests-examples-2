CREATE TABLE eats_automation_statistics.coverage_core_testsuite_builds (
    build_id                    VARCHAR(100) PRIMARY KEY,
    start_date                  NUMERIC,
    coverage_ratio              NUMERIC,
    endpoints_usage_stat_len    NUMERIC
);

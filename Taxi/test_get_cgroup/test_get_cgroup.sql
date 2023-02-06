INSERT INTO logs_errors_filters.cgroups (
    name,
    status,
    type,
    last_link
)
VALUES (
    'taxi_test-service_stable', 'ok', 'rtc', 'test_link'
);

INSERT INTO logs_errors_filters.filters (
    id,
    description,
    st_key,
    cgroup,
    creator,
    created
)
VALUES
(
    1, 'filter_1', 'TAXIPLATFORM-1', 'taxi_test-service_stable',
    'nevladov', '2019-09-03 10:00:00'::timestamp
);

INSERT INTO logs_errors_filters.base_queries (
    filter_id,
    field,
    matchstring
)
VALUES
(1, 'type', 'log'),
(1, 'text', 'error occurred');


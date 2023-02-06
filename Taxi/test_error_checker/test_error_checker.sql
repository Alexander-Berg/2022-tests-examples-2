INSERT INTO logs_errors_filters.cgroups (
    name,
    status,
    last_reason
)
VALUES (
    'taxi_imports',
    'ok',
    ''
),
(
    'taxi_logserrors',
    'warn',
    ''
),
(
    'taxi_billing_replication',
    'ok',
    ''
),
(
    'taxi_logs_from_yt',
    'ok',
    ''
);

INSERT INTO logs_errors_filters.juggler_checks (
    host,
    service,
    namespace,
    cgroup_name
)
VALUES (
    'test_host',
    'taxi_logerrors_cgroup_taxi_imports',
    'taxi_logserrors.production',
    'taxi_imports'
),
(
    'test_host',
    'taxi_logserrors_cgroup_taxi_logserrors',
    'taxi_logserrors.production',
    'taxi_logserrors'
),
(
    'test_host',
    'taxi_logserrors_cgroup_taxi_billing_replication',
    'taxi_logserrors.production',
    'taxi_billing_replication'
);

INSERT INTO logs_errors_filters.filters (
    id,
    description,
    st_key,
    cgroup,
    creator,
    created,
    threshold,
    suppress_related_errors
)
VALUES (
    1, 'filter_1', 'TAXIPLATFORM-1', 'taxi_imports',
    'nevladov', '2019-09-03 10:00:00'::timestamp, 0, False
),
(
    2, 'filter_2', 'TAXIPLATFORM-1', 'taxi_logserrors', 'nevladov',
    '2019-09-03 11:00:00'::timestamp, 0, False
),
(
    3, 'filter_3', 'TAXIPLATFORM-1', 'taxi_logs_from_yt', 'nevladov',
    '2019-09-03 12:00:00'::timestamp, 0, False
),
(
    4, 'filter_4', 'TAXIPLATFORM-1', 'taxi_billing_replication', 'nevladov',
    '2019-09-03 12:00:00'::timestamp, 0, False
),
(
    5, 'filter_5', 'TAXIPLATFORM-1', 'taxi_billing_replication', 'nevladov',
    '2019-09-03 12:00:00'::timestamp, 2, False
),
(
    6, 'filter_6_bad::', 'TAXIPLATFORM-1', 'taxi_billing_replication', 'nevladov',
    '2019-09-03 12:00:00'::timestamp, 2, False
);

INSERT INTO logs_errors_filters.base_queries (
    filter_id,
    field,
    matchstring
)
VALUES
(1, 'text', 'error'),
(2, 'text', 'error'),
(3, 'text', 'error'),
(4, 'text', 'error'),
(5, 'text', 'error'),
(6, 'text_bad:', 'skip');

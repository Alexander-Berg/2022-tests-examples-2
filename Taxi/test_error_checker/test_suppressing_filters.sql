INSERT INTO logs_errors_filters.cgroups (
    name,
    status,
    last_reason
)
VALUES (
    'taxi_hejmdal_stable',
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
    'taxi_logerrors_cgroup_taxi_hejmdal_stable',
    'taxi_logserrors.production',
    'taxi_hejmdal_stable'
);

INSERT INTO logs_errors_filters.filters (
    id,
    description,
    st_key,
    cgroup,
    creator,
    created,
    threshold,
    suppress_related_errors,
    filter_interval_minutes
)
VALUES (
    1, 'filter_1', 'TAXIPLATFORM-1', 'taxi_hejmdal_stable',
    'atsinin', '2022-07-19 10:00:00'::timestamp, 2, False, 5
),
(
    2, 'filter_2', 'TAXIPLATFORM-1', 'taxi_hejmdal_stable',
    'atsinin', '2022-07-19 11:00:00'::timestamp, 0, True, 15
),
(
    3, 'filter_3', 'TAXIPLATFORM-1', 'taxi_hejmdal_stable',
    'atsinin', '2022-07-19 11:00:00'::timestamp, 2, True, 30
);

INSERT INTO logs_errors_filters.base_queries (
    filter_id,
    field,
    matchstring
)
VALUES
(1, 'field1', 'value1'),
(1, 'field2', 'value2'),
(2, 'field3', 'value3'),
(2, 'field4', 'value4'),
(3, 'field5', 'value5'),
(3, 'field6', 'value6');

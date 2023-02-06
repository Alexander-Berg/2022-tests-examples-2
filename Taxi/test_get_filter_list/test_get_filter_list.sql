INSERT INTO logs_errors_filters.cgroups (
    name,
    status
)
VALUES (
    'taxi_billing_replication', 'ok'
),
(
    'taxi_billing_docs', 'ok'
),
(
    'taxi_logserrors', 'ok'
);

ALTER TABLE logs_errors_filters.filters DISABLE TRIGGER filters_set_enabled_at_tr;

INSERT INTO logs_errors_filters.filters (
    id,
    description,
    st_key,
    cgroup,
    creator,
    created,
    enabled_at
)
VALUES
(
    1, 'filter_1', 'TAXIPLATFORM-1', 'taxi_billing_replication',
    'nevladov', '2019-09-03 10:00:00'::timestamp, NULL
),
(
    2, 'filter_2', 'TAXIPLATFORM-1', 'taxi_billing_docs', 'shrek',
    '2019-09-03 11:00:00'::timestamp, NULL
),
(
    3, 'filter_3', 'TAXIPLATFORM-1', 'taxi_logserrors', 'nevladov',
    '2019-09-03 12:00:00'::timestamp, '2019-09-03 12:00:00'::timestamp
),
(
    4, 'filter_4', 'TAXIPLATFORM-1', 'taxi_billing_docs', 'nevladov',
    '2019-09-03 13:00:00'::timestamp, NULL
),
(
    5, 'filter_5', 'TAXIPLATFORM-1', NULL, 'nevladov',
    '2019-09-03 14:00:00'::timestamp, NULL
);

ALTER TABLE logs_errors_filters.filters ENABLE TRIGGER filters_set_enabled_at_tr;

INSERT INTO logs_errors_filters.base_queries (
    filter_id,
    field,
    matchstring
)
VALUES
(3, 'type', 'log'),
(3, 'text', 'error occurred');


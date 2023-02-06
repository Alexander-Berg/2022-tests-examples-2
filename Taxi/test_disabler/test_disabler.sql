INSERT INTO logs_errors_filters.cgroups (
    name,
    status
)
VALUES (
    'taxi_billing_replication', 'ok'
);

ALTER TABLE logs_errors_filters.filters DISABLE TRIGGER filters_set_enabled_at_tr;

INSERT INTO logs_errors_filters.filters (
    id,
    description,
    st_key,
    cgroup,
    creator,
    created,
    enabled,
    enabled_at,
    suppress_related_errors
)
VALUES
(
    1, 'filter_1', 'TAXIPLATFORM-1', 'taxi_billing_replication', 'nevladov',
    '2019-10-03 10:00:00'::timestamp,
    TRUE, '2019-10-03 10:00:00'::timestamp, False
),
(
    2, 'filter_2', 'TAXIPLATFORM-1', 'taxi_billing_replication', 'nevladov',
    '2019-09-03 11:00:00'::timestamp,
    TRUE, '2019-09-03 10:00:00'::timestamp, False
);

ALTER TABLE logs_errors_filters.filters ENABLE TRIGGER filters_set_enabled_at_tr;

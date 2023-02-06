INSERT INTO logs_errors_filters.cgroups (
    name,
    status
)
VALUES
    ('taxi_billing_replication', 'ok'),
    ('taxi_billing_docs', 'ok'),
    ('taxi_logserrors', 'ok');

INSERT INTO logs_errors_filters.filters (
    id,
    description,
    st_key,
    cgroup,
    creator
)
VALUES
(1, '', '', 'taxi_billing_replication', 'nevladov'),
(2, '', '', 'taxi_billing_docs', 'nevladov'),
(3, '', '', 'taxi_logserrors', 'nevladov'),
(4, '', '', 'taxi_billing_docs', 'nevladov');

UPDATE logs_errors_filters.cgroups
SET
    subscribers = '{"nevladov"}'
WHERE
    name = 'taxi_billing_replication';

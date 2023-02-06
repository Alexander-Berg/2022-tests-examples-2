INSERT INTO logs_errors_filters.cgroups (
    name,
    status
)
VALUES (
    'taxi_logserrors', 'ok'
),
(
    'taxi_imports', 'ok'
);

INSERT INTO logs_errors_filters.filters (
    id,
    description,
    st_key,
    cgroup,
    creator
)
VALUES
(1, '', '', 'taxi_logserrors', 'nevladov');

INSERT INTO logs_errors_filters.cgroups (
    name,
    status,
    subscribers
)
VALUES (
    'taxi_imports',
    'ok',
    '{"nevladov"}'
),
(
    'taxi_logserrors',
    'warn',
    '{"nevladov"}'
),
(
    'taxi_logs_from_yt',
    'ok',
    '{"nevladov"}'
);

INSERT INTO logs_errors_filters.juggler_checks (
    host,
    service,
    namespace,
    cgroup_name
)
VALUES (
    'logserrors.taxi.yandex.net',
    'taxi_logerrors_cgroup_taxi_imports',
    'taxi_logserrors.production',
    'taxi_imports'
),
(
    'logserrors.taxi.yandex.net',
    'taxi_logserrors_cgroup_taxi_logserrors',
    'taxi_logserrors.production',
    'taxi_logserrors'
),
(
    'logserrors.taxi.yandex.net',
    'taxi_logserrors_cgroup_taxi_exp',
    'taxi_logserrors.production',
    'taxi_exp'
);

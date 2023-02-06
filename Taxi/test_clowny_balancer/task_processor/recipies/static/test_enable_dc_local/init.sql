insert into
    balancers.upstreams (
        id,
        branch_id,
        service_id,
        awacs_backend_id,
        env
    )
values (
    11,
    21,
    31,
    'taxi_service-31_stable',
    'stable'
)
;

insert into
    balancers.namespaces (
        id,
        project_id,
        awacs_namespace,
        env,
        abc_quota_source
    )
values (
    51,
    150,
    'taxi-service-31',
    'stable',
    'taxiquotaypdefault'
)
;

insert into
    balancers.entry_points (
        id,
        namespace_id,
        awacs_upstream_id,
        protocol,
        dns_name,
        env
    )
values (
    41,
    51,
    'default',
    'http',
    'service-31.taxi.yandex.net',
    'stable'
)
;

insert into
    balancers.entry_points_upstreams (
        entry_point_id,
        upstream_id
    )
values (
    41,
    11
)
;

insert into
    balancers.upstreams (
        id,
        branch_id,
        service_id,
        awacs_backend_id,
        env
    )
values (
    1,
    2,
    3,
    'backend_man_pre',
    'prestable'
),
       (
    2,
    3,
    3,
    'backend_man',
    'stable'
),
       (
    3,
    3,
    3,
    'backend_sas',
    'stable'
),
       (
    4,
    3,
    3,
    'backend_vla',
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
    'taxi-service-3',
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
    'service-3.taxi.yandex.net',
    'stable'
)
;

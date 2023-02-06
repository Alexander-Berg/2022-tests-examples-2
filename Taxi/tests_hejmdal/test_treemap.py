def sort_items(items):
    return sorted(items, key=lambda x: x['id'])


async def test_treemap(taxi_hejmdal, load_json):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['tvm-rules-cache'],
    )
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['db-deps-cache'],
    )

    response = await taxi_hejmdal.post(
        'v1/health/treemap',
        json={'projects': [{'enabled': True, 'name': 'unknown_project'}]},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'INVALID_TREEMAP_SETTINGS',
        'message': 'invalid treemap settings',
    }

    response = await taxi_hejmdal.post('v1/health/treemap', json={})
    assert response.status_code == 200
    resp_json = response.json()
    assert sorted(resp_json.keys()) == [
        'items',
        'refresh_interval_sec',
        'timestamp',
    ]
    assert sort_items(resp_json['items']) == load_json(
        'treemap_default_settings.json',
    )
    assert resp_json['refresh_interval_sec'] == 60

    response = await taxi_hejmdal.post(
        'v1/health/treemap',
        json={
            'projects': [
                {'name': 'prj1', 'enabled': True},
                {'name': 'prj2', 'enabled': False},
            ],
            'checks_by_cluster_type': [
                {
                    'cluster_type': 'postgres',
                    'checks': [
                        {'name': 'hejmdal-pg-ram-usage', 'enabled': True},
                        {'name': 'Other checks', 'enabled': False},
                    ],
                },
            ],
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert sorted(resp_json.keys()) == [
        'items',
        'refresh_interval_sec',
        'timestamp',
    ]
    assert sort_items(resp_json['items']) == load_json(
        'treemap_prj1_filter1.json',
    )
    assert resp_json['refresh_interval_sec'] == 60

    response = await taxi_hejmdal.post(
        'v1/health/treemap',
        json={
            'projects': [
                {'name': 'prj1', 'enabled': False},
                {'name': 'prj2', 'enabled': True},
            ],
            'checks_by_cluster_type': [
                {
                    'cluster_type': 'nanny',
                    'checks': [
                        {'name': 'vhost-500', 'enabled': True},
                        {'name': 'Other checks', 'enabled': False},
                    ],
                },
            ],
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert sorted(resp_json.keys()) == [
        'items',
        'refresh_interval_sec',
        'timestamp',
    ]
    assert sort_items(resp_json['items']) == load_json(
        'treemap_prj2_filter1.json',
    )
    assert resp_json['refresh_interval_sec'] == 60

    response = await taxi_hejmdal.post(
        'v1/health/treemap',
        json={
            'projects': [
                {'name': 'prj1', 'enabled': False},
                {'name': 'prj2', 'enabled': True},
            ],
            'checks_by_cluster_type': [
                {
                    'cluster_type': 'nanny',
                    'checks': [
                        {'name': 'vhost-500', 'enabled': False},
                        {'name': 'Other checks', 'enabled': True},
                    ],
                },
            ],
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert sorted(resp_json.keys()) == [
        'items',
        'refresh_interval_sec',
        'timestamp',
    ]
    assert sort_items(resp_json['items']) == load_json(
        'treemap_prj2_filter2.json',
    )
    assert resp_json['refresh_interval_sec'] == 60

    response = await taxi_hejmdal.post(
        'v1/health/treemap',
        json={
            'projects_by_namespace': [
                {
                    'namespace': 'namespace1',
                    'projects': [{'name': 'prj1', 'enabled': True}],
                },
                {
                    'namespace': 'namespace2',
                    'projects': [
                        {'name': 'prj2', 'enabled': False},
                        {'name': 'prj3', 'enabled': True},
                    ],
                },
            ],
            'checks_by_cluster_type': [
                {
                    'cluster_type': 'nanny',
                    'checks': [
                        {'name': 'vhost-500', 'enabled': True},
                        {'name': 'Other checks', 'enabled': True},
                    ],
                },
            ],
            'tiers': [
                {'name': 'A', 'enabled': False},
                {'name': 'B', 'enabled': True},
                {'name': 'C', 'enabled': True},
                {'name': 'D', 'enabled': True},
                {'name': 'No tier', 'enabled': True},
            ],
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert sorted(resp_json.keys()) == [
        'items',
        'refresh_interval_sec',
        'timestamp',
    ]
    assert sort_items(resp_json['items']) == load_json(
        'treemap_prj13_filter3_namespace_tier.json',
    )
    assert resp_json['refresh_interval_sec'] == 60


async def test_treemap_settings(taxi_hejmdal, mockserver):
    @mockserver.json_handler('/clownductor/v1/projects/')
    async def _mock_projects(request):
        return [
            {'id': 2, 'name': 'prj2', 'namespace_id': 2},
            {'id': 1, 'name': 'prj1', 'namespace_id': 1},
            {'id': 3, 'name': 'prj3', 'namespace_id': 2},
        ]

    @mockserver.json_handler('/clownductor/v1/namespaces/retrieve/')
    async def _mock_namespaces(request):
        return {
            'namespaces': [
                {'id': 2, 'name': 'namespace2'},
                {'id': 1, 'name': 'namespace1'},
            ],
        }

    response = await taxi_hejmdal.get('v1/health/treemap/settings')
    assert response.status_code == 200
    assert response.json() == {
        'checks_by_cluster_type': [
            {
                'checks': [
                    {'enabled': True, 'name': 'atop'},
                    {'enabled': True, 'name': 'core-files'},
                    {'enabled': True, 'name': 'hejmdal-500-rps-low'},
                    {'enabled': True, 'name': 'hejmdal-bad-rps'},
                    {'enabled': True, 'name': 'hejmdal-ok-rps'},
                    {'enabled': True, 'name': 'hejmdal-rtc-cpu-usage'},
                    {'enabled': True, 'name': 'hejmdal-rtc-oom'},
                    {'enabled': True, 'name': 'hejmdal-rtc-ram-usage'},
                    {
                        'enabled': True,
                        'name': 'hejmdal-rtc-timings-cpu-aggregation',
                    },
                    {'enabled': True, 'name': 'hejmdal-timings-p95'},
                    {'enabled': True, 'name': 'hejmdal-timings-p98'},
                    {'enabled': True, 'name': 'iptruler'},
                    {'enabled': True, 'name': 'l7_balancer_cpu_usage'},
                    {'enabled': True, 'name': 'l7_balancer_cpu_wait_cores'},
                    {'enabled': True, 'name': 'l7_balancer_http_5xx'},
                    {'enabled': True, 'name': 'l7_balancer_logs_vol_usage'},
                    {'enabled': True, 'name': 'l7_balancer_mem_usage'},
                    {'enabled': True, 'name': 'pilorama-logs-lag'},
                    {'enabled': True, 'name': 'pilorama-running'},
                    {'enabled': True, 'name': 'push-client-status'},
                    {'enabled': True, 'name': 'strongbox_client'},
                    {'enabled': True, 'name': 'unispace'},
                    {'enabled': True, 'name': 'userver_congestion_control'},
                    {'enabled': True, 'name': 'vhost-499'},
                    {'enabled': True, 'name': 'vhost-500'},
                    {'enabled': True, 'name': 'virtual-meta'},
                    {'enabled': True, 'name': 'Other checks'},
                ],
                'cluster_type': 'nanny',
            },
            {
                'checks': [
                    {'enabled': True, 'name': 'hejmdal-pg-cpu-usage'},
                    {'enabled': True, 'name': 'hejmdal-pg-ram-usage'},
                    {'enabled': True, 'name': 'hejmdal-pg-disk-usage'},
                    {'enabled': True, 'name': 'hejmdal-pg-disk-decrease-slow'},
                    {'enabled': True, 'name': 'hejmdal-pg-disk-decrease-fast'},
                    {'enabled': True, 'name': 'Other checks'},
                ],
                'cluster_type': 'postgres',
            },
            {
                'checks': [
                    {'enabled': True, 'name': 'hejmdal-mongo-cpu-usage'},
                    {'enabled': True, 'name': 'hejmdal-mongo-ram-usage'},
                    {'enabled': True, 'name': 'hejmdal-mongo-disk-usage'},
                    {'enabled': True, 'name': 'hejmdal-mongo-is-alive'},
                    {'enabled': True, 'name': 'Other checks'},
                ],
                'cluster_type': 'mongo_mdb',
            },
            {
                'checks': [
                    {'enabled': True, 'name': 'hejmdal-redis-cpu-usage'},
                    {'enabled': True, 'name': 'hejmdal-redis-ram-usage'},
                    {'enabled': True, 'name': 'hejmdal-redis-disk-usage'},
                    {'enabled': True, 'name': 'Other checks'},
                ],
                'cluster_type': 'redis_mdb',
            },
            {
                'checks': [
                    {'enabled': True, 'name': 'atop'},
                    {'enabled': True, 'name': 'core-files'},
                    {'enabled': True, 'name': 'dns_local'},
                    {'enabled': True, 'name': 'hejmdal-500-rps-low'},
                    {'enabled': True, 'name': 'hejmdal-bad-rps'},
                    {'enabled': True, 'name': 'hejmdal-ok-rps'},
                    {'enabled': True, 'name': 'hejmdal-timings-p95'},
                    {'enabled': True, 'name': 'hejmdal-timings-p98'},
                    {'enabled': True, 'name': 'iptruler'},
                    {'enabled': True, 'name': 'load_average'},
                    {'enabled': True, 'name': 'nginx-alive'},
                    {'enabled': True, 'name': 'nginx-ratelimiter'},
                    {'enabled': True, 'name': 'oom'},
                    {'enabled': True, 'name': 'pilorama-logs-lag'},
                    {'enabled': True, 'name': 'pilorama-running'},
                    {'enabled': True, 'name': 'realsrv.slb_state'},
                    {'enabled': True, 'name': 'slb-alive'},
                    {
                        'enabled': True,
                        'name': 'statistics-client-get-fallbacks-error',
                    },
                    {'enabled': True, 'name': 'strongbox_client'},
                    {'enabled': True, 'name': 'vhost-499'},
                    {'enabled': True, 'name': 'vhost-500'},
                    {'enabled': True, 'name': 'virtual-meta'},
                    {'enabled': True, 'name': 'Other checks'},
                ],
                'cluster_type': 'conductor',
            },
            {
                'checks': [
                    {'enabled': True, 'name': 'atop'},
                    {'enabled': True, 'name': 'check-mongo-oplog'},
                    {'enabled': True, 'name': 'hejmdal-mongo-slow-queries'},
                    {'enabled': True, 'name': 'ipv6'},
                    {'enabled': True, 'name': 'load_average'},
                    {'enabled': True, 'name': 'memusage'},
                    {'enabled': True, 'name': 'mongo-conf'},
                    {'enabled': True, 'name': 'mongo-conn-current'},
                    {'enabled': True, 'name': 'mongo-rollback'},
                    {'enabled': True, 'name': 'mongocfg-alive'},
                    {'enabled': True, 'name': 'mongocfg-conf'},
                    {'enabled': True, 'name': 'mongocfg-repl-delay'},
                    {'enabled': True, 'name': 'mongodb-alive'},
                    {'enabled': True, 'name': 'mongodb-pool'},
                    {'enabled': True, 'name': 'mongos-alive'},
                    {'enabled': True, 'name': 'mongos-pool'},
                    {'enabled': True, 'name': 'oom'},
                    {'enabled': True, 'name': 'salt-minion'},
                    {'enabled': True, 'name': 'strongbox_client'},
                ],
                'cluster_type': 'mongo_lxc',
            },
            {
                'checks': [
                    {'enabled': True, 'name': 'atop'},
                    {'enabled': True, 'name': 'cron'},
                    {'enabled': True, 'name': 'dns_local'},
                    {'enabled': True, 'name': 'ipv6'},
                    {'enabled': True, 'name': 'load_average'},
                    {'enabled': True, 'name': 'logrotate'},
                    {'enabled': True, 'name': 'memusage'},
                    {'enabled': True, 'name': 'ntp_stratum'},
                    {'enabled': True, 'name': 'oom'},
                    {'enabled': True, 'name': 'pkgver-none'},
                    {'enabled': True, 'name': 'redis-cpu-usage'},
                    {'enabled': True, 'name': 'redis-ram-usage'},
                    {'enabled': True, 'name': 'redis-sys-ram-usage'},
                    {'enabled': True, 'name': 'redis_check'},
                    {'enabled': True, 'name': 'redis_check_groups'},
                    {'enabled': True, 'name': 'redis_errors'},
                    {'enabled': True, 'name': 'redis_migration'},
                    {'enabled': True, 'name': 'salt-minion'},
                    {'enabled': True, 'name': 'unispace'},
                    {'enabled': True, 'name': 'virtual-meta'},
                ],
                'cluster_type': 'redis_lxc',
            },
        ],
        'projects': [
            {'enabled': True, 'name': 'prj1'},
            {'enabled': True, 'name': 'prj2'},
            {'enabled': True, 'name': 'prj3'},
        ],
        'projects_by_namespace': [
            {
                'namespace': 'namespace1',
                'projects': [{'name': 'prj1', 'enabled': True}],
            },
            {
                'namespace': 'namespace2',
                'projects': [
                    {'name': 'prj2', 'enabled': True},
                    {'name': 'prj3', 'enabled': True},
                ],
            },
        ],
        'tiers': [
            {'name': 'A', 'enabled': True},
            {'name': 'B', 'enabled': True},
            {'name': 'C', 'enabled': True},
            {'name': 'D', 'enabled': True},
            {'name': 'No tier', 'enabled': True},
        ],
    }

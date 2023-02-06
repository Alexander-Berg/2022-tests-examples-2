import pytest


def _param(name, input_data, payload=None, extra=None, call_extras=None):
    return (name, input_data, payload, extra, call_extras or {})


@pytest.mark.config(
    CLOWNY_BALANCER_IO_QUOTA_DEFAULTS={
        'testing': [
            {'path': '/', 'value': 1},
            {'path': '/awacs', 'value': 1},
            {'path': '/logs', 'value': 1},
        ],
        'stable': [
            {'path': '/', 'value': 1},
            {'path': '/awacs', 'value': 2},
            {'path': '/logs', 'value': 2},
        ],
    },
)
@pytest.mark.parametrize(
    'cube_name, input_data, payload, extra, call_extras',
    [
        _param(
            'InternalFindModelsToRemove',
            {'namespace_id': 1},
            {
                'entry_point_ids': [1],
                'upstream_ids': [2],
                'awacs_namespace_id': 'test.net',
            },
        ),
        _param(
            'InternalFindModelsToRemove',
            {'namespace_id': 2},
            {
                'entry_point_ids': [2],
                'upstream_ids': [],
                'awacs_namespace_id': 'test-2.net',
            },
        ),
        _param(
            'InternalFindModelsToRemove',
            {'namespace_id': 3},
            {
                'entry_point_ids': [3],
                'upstream_ids': [],
                'awacs_namespace_id': 'test-3.net',
            },
        ),
        _param(
            'InternalFindModelsToRemove',
            {'namespace_id': 4},
            {
                'entry_point_ids': [],
                'upstream_ids': [],
                'awacs_namespace_id': '',
            },
        ),
        _param('InternalDeleteNamespace', {'namespace_id': 1}),
        _param('InternalDeleteEntryPoints', {'entry_point_ids': [1, 2]}),
        _param('InternalDeleteUpstreams', {'upstream_ids': [1, 2]}),
        _param(
            'InternalCreateEntryPoint',
            {
                'fqdn': 'test.fqdn',
                'protocol': 'http',
                'env': 'prestable',
                'namespace_id': 1,
            },
            {'entry_point_id': 10, 'awacs_namespace_id': 'test.net'},
        ),
        _param(
            'InternalCreateEntryPoint',
            {
                'fqdn': 'test.fqdn',
                'env': 'prestable',
                'protocol': 'https',
                'namespace_id': 1,
            },
            {'entry_point_id': 10, 'awacs_namespace_id': 'test.net'},
        ),
        _param(
            'InternalCreateEntryPoint',
            {
                'fqdn': 'test.fqdn',
                'env': 'prestable',
                'protocol': 'https',
                'is_external': True,
                'namespace_id': 6,
            },
            {'entry_point_id': 10, 'awacs_namespace_id': 'test-6.net'},
        ),
        _param(
            'InternalCreateEPULink', {'entry_point_id': 4, 'upstream_id': 1},
        ),
        _param(
            'InternalCollectForEPCreate',
            {'branch_id': 1},
            {'nanny_endpoint_set_id': 'some-endpointset-id'},
        ),
        _param(
            'InternalCollectForEPCreate',
            {'branch_id': 2},
            extra={
                'error_message': (
                    'Service some-2 has many endpointset ids: '
                    '[\'some-endpointset-id-2\', \'some-endpointset-id-3\'], '
                    'i cant determine what to use'
                ),
                'status': 'failed',
            },
        ),
        _param(
            'InternalSleepFor',
            {'sleep': 10, 'max_retries': 1},
            extra={'sleep_duration': 10, 'status': 'in_progress'},
        ),
        _param(
            'InternalSleepFor',
            {'sleep': 10, 'max_retries': 1},
            call_extras={'retries': 1},
        ),
        _param('InternalUpdateEntryPoint', {'entry_point_id': 4}),
        _param(
            'InternalUpdateEntryPoint',
            {'entry_point_id': 4, 'is_external': True},
        ),
        _param('InternalUpdateNamespace', {'namespace_id': 1}),
        _param(
            'InternalUpdateNamespace',
            {'namespace_id': 1, 'is_external': True},
        ),
        _param(
            'InternalGetIoInfo',
            {'env': 'testing'},
            {
                'io_info': [
                    {'path': '/', 'value': 1},
                    {'path': '/awacs', 'value': 1},
                    {'path': '/logs', 'value': 1},
                ],
            },
        ),
        _param(
            'InternalGetIoInfo',
            {'env': 'stable'},
            {
                'io_info': [
                    {'path': '/', 'value': 1},
                    {'path': '/awacs', 'value': 2},
                    {'path': '/logs', 'value': 2},
                ],
            },
        ),
        _param(
            'InternalGetNamespaces',
            {'service_id': 1},
            {'namespace_ids': ['test.net', 'test-2.net']},
        ),
        _param(
            'InternalGetNamespaces',
            {'service_id': 1, 'branch_ids': [1, 22]},
            {'namespace_ids': ['test.net', 'test-2.net']},
        ),
        _param(
            'InternalGetNamespaces',
            {'service_id': 1, 'branch_ids': [100, 22]},
            {'namespace_ids': []},
        ),
        _param(
            'InternalGetEntrypointInfo',
            {'entry_point_id': 1},
            {
                'awacs_namespace_id': 'test.net',
                'dns_name': 'test.net',
                'awacs_domain_ids': [],
                'awacs_upstream_ids': ['default'],
                'entry_point_ids': [1],
                'upstream_ids': [1, 2],
                'awacs_backend_ids': ['some'],
            },
        ),
        _param(
            'InternalGetAwacsInfoBranch',
            {'clown_service_id': 1, 'clown_branch_id': 2},  # prestable branch
            {'awacs_backend_id': 'some', 'awacs_namespace_id': 'test.net'},
        ),
    ],
)
async def test_cubes(
        mock_nanny_yp,
        mock_clownductor,
        call_cube,
        cube_name,
        input_data,
        payload,
        extra,
        call_extras,
):
    @mock_nanny_yp('/endpoint-sets/ListEndpointSets/')
    def _nanny_yp_handler(request):
        _region = request.json['cluster']
        _service_id = request.json['service_id']

        endpoint_sets = [
            {
                'meta': {
                    'id': 'some-endpointset-id',
                    'serviceId': 'taxi_service_stable',
                },
                'region': 'SAS',
            },
            {
                'meta': {
                    'id': 'some-endpointset-id',
                    'serviceId': 'taxi_service_stable',
                },
                'region': 'VLA',
            },
            {
                'meta': {'id': 'some-endpointset-id-2', 'serviceId': 'some-2'},
                'region': 'SAS',
            },
            {
                'meta': {'id': 'some-endpointset-id-3', 'serviceId': 'some-2'},
                'region': 'VLA',
            },
        ]
        return {
            'endpointSets': [
                x
                for x in endpoint_sets
                if x['meta']['serviceId'] == _service_id
                and x['region'] == _region
            ],
        }

    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        branch_id = int(request.query['branch_ids'].split(',')[0])
        branches = [
            {
                'id': 1,
                'env': 'stable',
                'direct_link': 'taxi_service_stable',
                'name': '',
                'service_id': 0,
            },
            {
                'id': 2,
                'env': 'stable',
                'direct_link': 'some-2',
                'name': '',
                'service_id': 0,
            },
        ]
        return [x for x in branches if x['id'] == branch_id]

    response = await call_cube(cube_name, input_data, **call_extras)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    if extra is not None:
        result.update(extra)
    assert response == result


@pytest.mark.parametrize(
    'cube_name, input_data, expected_ids',
    [
        (
            'InternalDeleteNamespace',
            {'namespace_id': 1},
            {
                'deleted': [('namespaces', [1])],
                'stayed': [
                    ('namespaces', [2, 3, 4, 5, 6]),
                    ('entry_points', [1, 2, 3, 4]),
                    ('upstreams', [1, 2]),
                ],
            },
        ),
        (
            'InternalDeleteEntryPoints',
            {'entry_point_ids': [1]},
            {
                'deleted': [('entry_points', [1])],
                'stayed': [
                    ('namespaces', [1, 2, 3, 4, 5, 6]),
                    ('entry_points', [2, 3, 4]),
                    ('upstreams', [1, 2]),
                ],
            },
        ),
        (
            'InternalDeleteUpstreams',
            {'upstream_ids': [1]},
            {
                'deleted': [('upstreams', [1])],
                'stayed': [
                    ('namespaces', [1, 2, 3, 4, 5, 6]),
                    ('entry_points', [1, 2, 3, 4]),
                    ('upstreams', [2]),
                ],
            },
        ),
    ],
)
async def test_deleting(
        web_context, call_cube, cube_name, input_data, expected_ids,
):
    await call_cube(cube_name, input_data)

    # check deleted items
    for table_name, ids in expected_ids['deleted']:
        rows = await web_context.pg.secondary.fetch(
            f'SELECT id, deleted_at '
            f'FROM balancers.{table_name} WHERE is_deleted = TRUE',
        )
        assert [x['id'] for x in rows] == ids, table_name
        assert all(x['deleted_at'] is not None for x in rows)

    # check non deleted items
    for table_name, ids in expected_ids['stayed']:
        rows = await web_context.pg.secondary.fetch(
            f'SELECT id, deleted_at '
            f'FROM balancers.{table_name} WHERE is_deleted != TRUE',
        )
        assert [x['id'] for x in rows] == ids, table_name
        assert all(x['deleted_at'] is None for x in rows)

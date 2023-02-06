import pytest

from testsuite.utils import matching


class MaybeTicket(matching.AnyString):
    def __eq__(self, other):
        return super().__eq__(other) and other in {'', 'TAXIADMIN-1'}


@pytest.fixture(name='load_recipe')
def _load_recipe(load_yaml, task_processor):
    def do_it():
        task_processor.load_recipe(
            load_yaml('AllocateExternalL3Addresses.yaml')['data'],
        )
        task_processor.load_recipe(
            load_yaml('BalancerReallocateAllPods.yaml')['data'],
        )
        return task_processor.load_recipe(
            load_yaml('EntryPointOpenToWorld.yaml')['data'],
        )

    return do_it


@pytest.fixture(name='job_checker')
def _job_checker(task_processor, run_job_common):
    async def do_it(job):
        await run_job_common(job, sleep_is_expected=True)
        assert job.job_vars == {
            'entry_point_id': 1,
            'namespace_id': 1,
            'abc_service_slug': 'taxi_abc_service',
            'additional_fqdns': ['external-yandex.ru'],
            'allocating_external_addresses_job_id': 2,
            'author': 'd1mbas',
            'awacs_cert_id': 'existing-cert-ext',
            'awacs_domain_id': 'awacs-domain-1',
            'awacs_namespace_id': 'awacs-ns-1',
            'cert_type': 'EXTERNAL',
            'ipv4': ['127.0.0.1'],
            'ipv6': ['2a02:6b8:0:3400:0:71d:0:4af', '2a02:6b8::330'],
            'original_ipv6': '2a02:6b8:0:3400:0:71d:0:4af',
            'l3mgr_service_id': '123',
            'origin_fqdn': 'service-fqdn.net',
            'puncher_source': 'any',
            'reallocating_balancer_pods': 3,
            'sectask_ticket': 'SECTASK-1',
            'st_ticket': MaybeTicket(),
        }

        assert [x.id for x in task_processor.jobs.values()] == [1, 2, 3]

    return do_it


@pytest.mark.usefixtures(
    'open_to_world_mocks',
    'allocate_l3_addresses_mocks',
    'reallocate_balancer_pods_mocks',
    'mock_clownductor_handlers',
)
async def test_recipe(load_recipe, job_checker):
    recipe = load_recipe()
    job = await recipe.start_job(
        job_vars={
            'entry_point_id': 1,
            'namespace_id': 1,
            'awacs_namespace_id': 'awacs-ns-1',
            'awacs_cert_id': 'existing-cert-ext',
            'awacs_domain_id': 'awacs-domain-1',
            'cert_type': 'EXTERNAL',
            'abc_service_slug': 'taxi_abc_service',
            'l3mgr_service_id': '123',
            'origin_fqdn': 'service-fqdn.net',
            'additional_fqdns': ['external-yandex.ru'],
            'author': 'd1mbas',
            'puncher_source': 'any',
            'st_ticket': 'TAXIADMIN-1',
        },
        initiator='clowny-balancer',
    )
    await job_checker(job)


@pytest.mark.usefixtures(
    'open_to_world_mocks',
    'allocate_l3_addresses_mocks',
    'reallocate_balancer_pods_mocks',
    'mock_clownductor_handlers',
)
@pytest.mark.parametrize(
    'entry_point_id, additional_fqdns, expected_status',
    [
        (2, None, 404),
        (1, ['external-yandex.ru'], 200),
        (1, ['service-fqdn.net', 'external-yandex.ru'], 400),
        (1, ['http://external-yandex.ru'], 400),
    ],
)
@pytest.mark.parametrize('use_drafts', [True, False])
async def test_endpoint(
        mockserver,
        mock_clownductor,
        taxi_clowny_balancer_web,
        job_checker,
        task_processor,
        load_recipe,
        get_entry_point,
        get_namespace,
        entry_point_id,
        additional_fqdns,
        expected_status,
        use_drafts,
        mock_get_project,
):
    @mock_clownductor('/api/projects')
    def _project(_):
        return [
            {
                'id': 1,
                'yp_quota_abc': 'taxi_abc_service',
                'namespace_id': 1,
                'name': 'taxi',
            },
        ]

    @mockserver.json_handler('/client-awacs/api/GetL3Balancer/')
    def _l3_balancer(_):
        return {'l3Balancer': {'spec': {'l3mgrServiceId': '123'}}}

    load_recipe()

    if not use_drafts:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/open-to-world/',
            json={
                'entry_point_id': entry_point_id,
                'additional_fqdns': additional_fqdns,
            },
            headers={'X-Yandex-Login': 'd1mbas'},
        )
        assert response.status == expected_status, await response.text()
        if expected_status != 200:
            assert not task_processor.jobs
            return

    else:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/open-to-world/check/',
            json={
                'entry_point_id': entry_point_id,
                'additional_fqdns': additional_fqdns,
            },
            headers={
                'X-Yandex-Login': 'd1mbas',
                'X-YaTaxi-Draft-Tickets': 'TAXIADMIN-1',
            },
        )
        result = await response.json()
        assert response.status == expected_status, result
        if expected_status != 200:
            assert not task_processor.jobs
            return

        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/open-to-world/apply/',
            json=result['data'],
            headers={
                'X-Yandex-Login': 'd1mbas',
                'X-YaTaxi-Draft-Tickets': 'TAXIADMIN-1',
            },
        )
        assert response.status == expected_status, await response.text()

    data = await response.json()
    job = task_processor.job(data['job_id'])
    await job_checker(job)

    entry_point = await get_entry_point(entry_point_id)
    assert entry_point.is_external
    namespace = await get_namespace(entry_point.namespace_id)
    assert namespace.is_external

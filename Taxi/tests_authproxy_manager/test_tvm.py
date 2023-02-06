import pytest


@pytest.fixture(name='mocks')
def _mocks(load_json, mockserver):
    @mockserver.json_handler('/clownductor/v1/projects/')
    async def _mock_projects(request):
        assert request.query == {}
        return load_json('clownductor_projects_response.json')

    @mockserver.json_handler('/clownductor/v1/services/')
    async def _mock_services(request):
        assert request.query == {'project_id': '39'}
        return load_json('clownductor_services_response.json')

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    async def _mock_service_values(request):
        service_id = request.query['service_id']
        assert request.query == {'service_id': service_id}

        if service_id == '354070':
            service = 'clownductor'
        elif service_id == '354071':
            service = 'statistics'
        elif service_id == '354072':
            service = 'clowny_balancer'
        else:
            assert False, f'service_id={service_id}'
        return load_json(f'clownductor_service_values_response_{service}.json')

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    async def _mock_services_retrieve(request):
        assert request.json == {
            'limit': 19,
            'clown_ids': [354070, 354071, 354072],
        }
        return {'services': []}

    @mockserver.json_handler('/clowny-balancer/balancers/v1/service/get/')
    async def _mock_balancers_service_get(request):
        service_id = request.query['service_id']
        assert service_id in {'354070', '354071', '354072'}
        assert request.query == {'service_id': service_id}

        if service_id == '354072':
            return load_json('clowny_balancer_response.json')

        return {'namespaces': []}

    yield


@pytest.mark.config(AUTHPROXY_MANAGER_CLOWNY_SERVICES_RETRIEVE_BATCH_SIZE=19)
async def test_tvm_services(authproxy_manager, mocks):

    response = await authproxy_manager.v1_tvm_service()
    assert response.status == 200
    assert sorted(response.json()['services'], key=lambda x: x['id']) == [
        {'hostnames': [], 'id': 2345, 'name': 'authproxy-manager'},
        {'hostnames': [], 'id': 1000000, 'name': 'api-proxy-manager'},
        {
            'hostnames': ['clownductor.taxi.yandex.net'],
            'id': 1000001,
            'name': 'clownductor',
        },
        {
            'hostnames': ['clowny-balancer.new.taxi.yandex.net'],
            'id': 1000002,
            'name': 'clowny-balancer',
        },
        {'hostnames': [], 'id': 1000003, 'name': 'clowny-perforator'},
        {'hostnames': [], 'id': 1000004, 'name': 'staff-production'},
        {
            'hostnames': ['statistics.taxi.yandex.net'],
            'id': 1000005,
            'name': 'statistics',
        },
    ]


@pytest.mark.config(AUTHPROXY_MANAGER_CLOWNY_SERVICES_RETRIEVE_BATCH_SIZE=19)
async def test_adjust_hostname(
        authproxy_manager, taxi_authproxy_manager, mocks,
):
    async def adjust(url: str) -> str:
        response = await taxi_authproxy_manager.post(
            '/v1/hints/url',
            json={'url': url},
            headers={'content-type': 'application/json'},
        )
        assert response.status == 200
        return response.json()['url-adjusted']

    adjusted = await adjust('clownductor.taxi.tst.yandex.net')
    assert adjusted == 'clownductor.taxi.yandex.net'

    adjusted = await adjust('http://clownductor.taxi.tst.yandex.net')
    assert adjusted == 'http://clownductor.taxi.yandex.net'

    adjusted = await adjust('http://clownductor.taxi.tst.yandex.net/foo/bar')
    assert adjusted == 'http://clownductor.taxi.yandex.net/foo/bar'

    adjusted = await adjust('https://clownductor.taxi.tst.yandex.net')
    assert adjusted == 'https://clownductor.taxi.yandex.net'

    adjusted = await adjust('https://clownductor.taxi.unknown.yandex.net')
    assert adjusted == 'https://clownductor.taxi.unknown.yandex.net'

    adjusted = await adjust('https://clowny-balancer.new.taxi.tst.yandex.net')
    assert adjusted == 'https://clowny-balancer.new.taxi.yandex.net'

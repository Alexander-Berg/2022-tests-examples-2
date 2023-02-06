import dataclasses

import pytest


@dataclasses.dataclass
class DNSResolverMockResult:
    cname: str


@pytest.fixture
def call_cube_client(web_app_client):
    return web_app_client


@pytest.mark.parametrize(
    'cube_name, input_data, payload',
    [
        (
            'DNSCreateAlias',
            {
                'alias': 'test-fqdn',
                'canonical_name': 'test-fqdn.taxi-yp.yandex.net',
            },
            None,
        ),
        (
            'DNSCreateRecord',
            {'fqdn': 'test-fqdn', 'ipv6': '2a02:6b8:0:3400:0:71d:0:176'},
            None,
        ),
        (
            'DNSDeleteRecord',
            {'fqdn': 'test-fqdn', 'ipv6': '2a02:6b8:0:3400:0:71d:0:176'},
            None,
        ),
        ('DNSCreateARecord', {'fqdn': 'test-fqdn', 'ipv4': '127.0.0.1'}, None),
        ('DNSCreateCNAMERecord', {'left_side': 'A', 'right_side': 'B'}, None),
        (
            'DNSCreateCNAMERecord',
            {'left_side': 'A', 'right_sides': ['B1', 'B2']},
            None,
        ),
    ],
)
async def test_cubes(
        dns_mockserver, call_cube, cube_name, input_data, payload,
):
    dns_mockserver()

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    assert response == result


@pytest.mark.parametrize(
    'input_data, payload',
    [
        ({'service_id': 1, 'env': 'unstable'}, {'host': 'host.yp.net'}),
        (
            {'service_id': 1, 'env': 'unstable', 'branch_name': 'ucustom'},
            {'host': 'host.ucustom.yp.net'},
        ),
    ],
)
async def test_init_balancer_alias(
        mock_clownductor, call_cube, input_data, payload,
):
    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        assert dict(request.query) == {'service_id': '1'}
        branches = [
            {
                'env': 'unstable',
                'id': 1,
                'name': 'unstable',
                'direct_link': '',
                'service_id': 0,
            },
        ]
        if 'branch_name' in input_data:
            branches.append(
                {
                    'env': 'unstable',
                    'id': 2,
                    'name': input_data['branch_name'],
                    'direct_link': '',
                    'service_id': 0,
                },
            )
        return branches

    @mock_clownductor('/v1/hosts/')
    def _hosts_handler(request):
        host = 'host.yp.net'
        branch_id = int(request.query['branch_id'])
        if branch_id == 2:
            host = 'host.ucustom.yp.net'
        return [{'branch_id': branch_id, 'name': host}]

    cube_name = 'InternalCubeInitBalancerAlias'
    response = await call_cube(cube_name, input_data)

    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    assert response == result
    assert _branches_handler.times_called == 1
    assert _hosts_handler.times_called == 1


async def test_resolve_alias(call_cube, patch):
    @patch('aiodns.DNSResolver.query')
    async def _query(host, qtype):
        assert host == 'alias.taxi.dev.yandex.net'
        assert qtype == 'CNAME'
        return DNSResolverMockResult('alias-1.yp-c.yandex.net')

    response = await call_cube(
        'DNSResolveAlias', {'alias': 'alias.taxi.dev.yandex.net'},
    )
    assert response == {
        'payload': {'host': 'alias-1.yp-c.yandex.net'},
        'status': 'success',
    }
    assert len(_query.calls) == 1


async def test_delete_alias(call_cube, dns_mockserver):
    mock = dns_mockserver()
    response = await call_cube(
        'DNSDeleteAlias',
        {
            'alias': 'alias.taxi.dev.yandex.net',
            'canonical_name': 'alias-1.taxi',
        },
    )
    assert response == {'status': 'success'}
    assert mock.times_called == 1
    assert mock.next_call()['request'].json == {
        'primitives': [
            {
                'data': 'alias-1.taxi',
                'name': 'alias.taxi.dev.yandex.net',
                'operation': 'delete',
                'type': 'CNAME',
            },
        ],
    }

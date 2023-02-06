import ipaddress
import urllib.parse

import multidict
import pytest

from testsuite.utils import http


def _form(request):
    charset = 'utf-8'
    items = urllib.parse.parse_qsl(
        request.get_data().rstrip().decode(charset),
        keep_blank_values=True,
        encoding=charset,
    )
    return multidict.MultiDict(items)


@pytest.mark.parametrize(
    'cube_name, input_data, payload',
    [
        (
            'L3MGRDisableBalancer',
            {'l3mgrServiceId': '1234'},
            {'l3_empty_config_id': '76220'},
        ),
        (
            'L3MGRWaitForEmptyServiceActivation',
            {'l3mgrServiceId': '1234', 'config_id': '76220'},
            None,
        ),
        ('L3MGRHideService', {'l3mgrServiceId': '8780'}, None),
        (
            'L3MGRFetchIpv6',
            {'l3mgrServiceId': '8780'},
            {'ipv6': '2a02:6b8:0:3400:0:71d:0:176'},
        ),
        (
            'L3MGRAdd443Port',
            {'l3mgr_service_id': '123'},
            {'l3mgr_config_id': '1234', 'l3_update_succeeded': True},
        ),
        (
            'L3MGRDeployConfiguration',
            {'l3mgr_service_id': '123', 'l3mgr_config_id': '1234'},
            None,
        ),
        (
            'L3MGRWaitConfigActivated',
            {'l3mgr_service_id': '123', 'l3mgr_config_id': '1234'},
            None,
        ),
        (
            'L3MGRCreateConfigForVsIds',
            {'l3mgr_service_id': '123', 'created_vs_ids': ['1234', '12345']},
            {'l3mgr_config_id': '1234', 'l3_update_succeeded': True},
        ),
        (
            'L3MGRFetchIps',
            {'l3mgr_service_id': '123'},
            {'ipv4': [], 'ipv6': ['2a02:6b8:0:3400:0:71d:0:176']},
        ),
    ],
)
async def test_cubes(
        l3mgr_mockserver, call_cube, cube_name, input_data, payload,
):
    mocker = l3mgr_mockserver()
    response = await call_cube(cube_name, input_data)
    expected = {'status': 'success'}
    if payload is not None:
        expected['payload'] = payload
    assert response == expected

    if cube_name == 'L3MGRDeployConfiguration':
        assert mocker.times_called == 1


class _L3MgrMock:
    def __init__(self, mockserver, mock_data):
        self.services = mock_data['services']

        @mockserver.json_handler(
            r'^/l3mgr/service/(?P<srv_id>\d+)$', regex=True,
        )
        def _get_service(request, srv_id):
            if request.method == 'GET':
                for srv in self.services:
                    if str(srv['id']) == srv_id:
                        return srv
            return http.make_response(status=404)

        @mockserver.json_handler(
            r'^/l3mgr/service/(?P<srv_id>\d+)/vs$', regex=True,
        )
        def _post_service_vs(request, srv_id):
            if request.method == 'POST':
                for srv in self.services:
                    if str(srv['id']) == srv_id:
                        _req = _form(request)
                        new_vs = {
                            'id': max(x['id'] for x in srv['vs']) + 1,
                            'ip': _req['ip'],
                            'port': int(_req['port']),
                            'rs': [int(x) for x in _req.getall('rs')],
                            'group': _req.getall('group'),
                        }
                        srv['vs'].append(new_vs)
                        return http.make_response(json={'object': new_vs})
            return http.make_response(status=404)

        @mockserver.json_handler('/l3mgr/abc/abc_service/getip')
        def _get_ip(request):
            _request = _form(request)
            assert _request['external'] == 'True'
            return {
                'object': (
                    '127.0.0.1'
                    if _request['v4'] == 'True'
                    else '2a02:6b8::38b'
                ),
            }


@pytest.fixture(name='l3mgr_mock')
def _l3mgr_mock(mockserver, load_yaml):
    return _L3MgrMock(mockserver, load_yaml('l3mgr_mock_data.yaml'))


@pytest.mark.parametrize(
    'cube_name, input_data, payload, is_v4',
    [
        pytest.param(
            'L3MGRAddExternalIpv4',
            {
                'abc_service_slug': 'abc_service',
                'l3mgr_service_id': '1',
                'fqdn': 'fqdn.net',
            },
            {'new_vs_ids': ['1', '2', '3', '4'], 'l3_update_succeeded': True},
            True,
        ),
        pytest.param(
            'L3MGRAddExternalIpv6',
            {
                'abc_service_slug': 'abc_service',
                'l3mgr_service_id': '1',
                'fqdn': 'fqdn.net',
                'created_new_vs_ids': ['12345'],
            },
            {
                'new_vs_ids': ['1', '12345', '2', '3', '4'],
                'l3_update_succeeded': True,
            },
            False,
        ),
    ],
)
async def test_allocate_cubes(
        call_cube, l3mgr_mock, cube_name, input_data, payload, is_v4,
):
    response = await call_cube(cube_name, input_data)
    expected = {'status': 'success'}
    if payload is not None:
        expected['payload'] = payload
    assert response == expected

    assert len(l3mgr_mock.services) == 1
    assert len(l3mgr_mock.services[0]['vs']) == 4

    new = l3mgr_mock.services[0]['vs'][2:]
    assert sorted(x['port'] for x in new) == [80, 443]
    assert all(
        ipaddress.ip_address(x['ip']).version == (4 if is_v4 else 6)
        for x in new
    )


async def test_allocate_in_chain(call_cube, l3mgr_mock):
    response = await call_cube(
        'L3MGRAddExternalIpv4',
        {
            'abc_service_slug': 'abc_service',
            'l3mgr_service_id': '1',
            'fqdn': 'fqdn.net',
        },
    )
    assert response['payload'] == {
        'new_vs_ids': ['1', '2', '3', '4'],
        'l3_update_succeeded': True,
    }

    response = await call_cube(
        'L3MGRAddExternalIpv6',
        {
            'abc_service_slug': 'abc_service',
            'l3mgr_service_id': '1',
            'fqdn': 'fqdn.net',
            'created_new_vs_ids': response['payload']['new_vs_ids'],
        },
    )
    assert response['payload'] == {
        'new_vs_ids': ['1', '2', '3', '4', '5', '6'],
        'l3_update_succeeded': True,
    }

    assert len(l3mgr_mock.services) == 1
    assert len(l3mgr_mock.services[0]['vs']) == 6

    def _check(new_vs, ip_v):
        assert sorted(x['port'] for x in new_vs) == [80, 443]
        assert all(
            (ipaddress.ip_address(x['ip']).version == ip_v) for x in new_vs
        )

    _check(l3mgr_mock.services[0]['vs'][2:4], 4)
    _check(l3mgr_mock.services[0]['vs'][4:], 6)

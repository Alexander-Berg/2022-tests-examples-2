import pytest


def _param(cube_name, input_data, payload=None, extras=None):
    return cube_name, input_data, payload, extras


@pytest.mark.parametrize(
    'cube_name, input_data, payload, extras',
    [
        _param(
            'AwacsBalancerGetBalancerIds',
            {'awacs_namespace_id': 'non-existing'},
            {'balancer_man': '', 'balancer_sas': '', 'balancer_vla': ''},
        ),
        _param(
            'AwacsBalancerGetBalancerIds',
            {'awacs_namespace_id': 'existing'},
            {
                'balancer_man': 'existing_man',
                'balancer_sas': '',
                'balancer_vla': '',
            },
        ),
        _param(
            'AwacsBalancerUpdateYamlForDomain',
            {'awacs_namespace_id': 'existing', 'balancer_id': 'existing_man'},
        ),
        _param(
            'AwacsBalancerChangeOwners',
            {
                'namespace_id': 'ns1',
                'balancer_id': 'some_balancer',
                'logins': ['d1mbas', 'oxcd8o'],
                'groups': ['some_group'],
            },
        ),
        _param(
            'AwacsBalancerAddHTTPS',
            {'namespace_id': 'ns1', 'balancer_id': 'b1'},
        ),
        _param(
            'AwacsBalancerAddHTTPS',
            {'namespace_id': 'ns1', 'balancer_id': 'b2'},
        ),
        _param(
            'AwacsBalancerWaitFor',
            {'namespace_id': 'ns1', 'balancer_id': 'b1'},
        ),
        _param(
            'AwacsBalancerWaitFor',
            {'namespace_id': 'ns1', 'balancer_id': 'b2'},
            extras={'sleep_duration': 10, 'status': 'in_progress'},
        ),
        _param(
            'AwacsBalancerDelete',
            {'namespace_id': 'ns1', 'balancer_id': 'b1'},
        ),
    ],
)
async def test_cube(
        mockserver, call_cube, cube_name, input_data, payload, extras,
):
    @mockserver.json_handler('/client-awacs/api/ListBalancers/')
    def _list_balancers_handler(request):
        if request.json['namespaceId'] == 'non-existing':
            return {'balancers': []}
        return {
            'balancers': [
                {
                    'meta': {
                        'id': 'existing_man',
                        'location': {
                            'yp_cluster': 'MAN',
                            'type': 'YP_CLUSTER',
                        },
                    },
                },
            ],
        }

    @mockserver.json_handler('/client-awacs/api/GetBalancer/')
    def _get_balancer_handler(request):
        balancer_id = request.json['id']
        return {
            'balancer': {
                'meta': {
                    'version': '123',
                    'auth': {'staff': {'owners': {'logins': ['d1mbas']}}},
                    'id': balancer_id,
                    'namespaceId': request.json['namespaceId'],
                },
                'spec': {
                    'yandex_balancer': {
                        'config': {
                            'l7_macro': (
                                {'https': {}} if balancer_id == 'b2' else {}
                            ),
                        },
                        'yaml': 'some',
                    },
                },
                'status': {
                    'active': {
                        'status': 'False' if balancer_id == 'b2' else 'True',
                    },
                    'validated': {'status': 'False', 'message': 'failed'},
                },
            },
        }

    @mockserver.json_handler('/client-awacs/api/UpdateBalancer/')
    def _update_balancer_handler(request):
        data = request.json
        assert data['meta']['version'] == '123'
        if cube_name == 'AwacsBalancerUpdateYamlForDomain':
            l7_macro = data['spec']['yandexBalancer']['config']['l7Macro']
            assert l7_macro == {
                'includeDomains': {},
                'healthCheckReply': {},
                'announceCheckReply': {
                    'urlRe': '/ping',
                    'useUpstreamHandler': True,
                },
            }
            assert 'yaml' not in data['spec']['yandexBalancer']
        if cube_name == 'AwacsBalancerChangeOwners':
            assert data['meta']['auth']['staff']['owners'] == {
                'logins': ['d1mbas', 'oxcd8o'],
                'groupIds': ['some_group'],
            }
        return {'balancer': data}

    @mockserver.json_handler('/client-awacs/api/RemoveBalancer/')
    def _delete_balancer_handler(request):
        assert request.json == {
            'id': 'b1',
            'namespaceId': 'ns1',
            'version': '123',
            'mode': 'AUTOMATIC',
        }
        return {}

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    if extras is not None:
        result.update(extras)
    assert response == result

    if cube_name == 'AwacsBalancerAddHTTPS':
        if input_data['balancer_id'] == 'b1':
            assert _update_balancer_handler.times_called == 1
        elif input_data['balancer_id'] == 'b2':
            assert _update_balancer_handler.times_called == 0

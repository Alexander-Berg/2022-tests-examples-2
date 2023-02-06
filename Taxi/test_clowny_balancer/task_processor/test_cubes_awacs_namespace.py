import pytest


@pytest.mark.parametrize(
    'cube_name, input_data, payload, extras',
    [
        (
            'AwacsNamespaceChangeOwners',
            {'namespace_id': 'ns1', 'logins': ['d1mbas']},
            None,
            None,
        ),
        (
            'AwacsNamespaceDelete',
            {'namespace_id': 'ns1', 'delete_empty': True},
            {'namespace_id': ''},
            None,
        ),
        (
            'AwacsNamespaceDelete',
            {'namespace_id': 'ns1'},
            {'namespace_id': ''},
            None,
        ),
        (
            'AwacsNamespaceDelete',
            {'namespace_id': 'ns2'},
            {'namespace_id': ''},
            None,
        ),
        (
            'AwacsNamespaceDelete',
            {'namespace_id': 'ns3', 'delete_empty': True},
            {'namespace_id': 'ns3'},
            None,
        ),
        (
            'AwacsNamespaceUpdate',
            {'namespace_id': 'ns1', 'service_abc': 'abc-slug'},
            None,
            None,
        ),
    ],
)
async def test_cubes(
        mockserver,
        call_cube,
        cube_name,
        input_data,
        payload,
        extras,
        abc_mockserver,
):
    abc_mockserver(services=True)

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_handler(request):
        return {
            'namespace': {
                'status': {'active': {'status': 'True'}},
                'meta': {'id': input_data['namespace_id'], 'version': '1'},
            },
        }

    @mockserver.json_handler('/client-awacs/api/UpdateNamespace/')
    def _update_handler(request):
        data = request.json
        if cube_name == 'AwacsNamespaceChangeOwners':
            assert data['meta']['auth']['staff']['owners'] == {
                'logins': ['d1mbas'],
            }
        if cube_name == 'AwacsNamespaceUpdate':
            assert data['meta']['abcServiceId'] == 3155
        return {'namespace': data}

    @mockserver.json_handler('/client-awacs/api/RemoveNamespace/')
    def _delete_handler(request):
        assert request.json == {'id': 'ns3', 'version': '1'}
        return {}

    @mockserver.json_handler('/client-awacs/api/ListBackends/')
    def _list_handler(request):
        namespace_id = request.json['namespaceId']
        if namespace_id == 'ns3':
            return {'backends': []}
        backend = {'backends': [{'meta': {'id': 'some_backend'}}]}
        if namespace_id == 'ns2':
            backend['backends'].append({'meta': {'id': 'rtc_balancer_some'}})
        return backend

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    result.update(extras or {})
    assert response == result

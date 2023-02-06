import pytest


@pytest.mark.parametrize(
    'test_uid,conf_effective',
    [('12345', True), ('4444', True), ('5555', True), ('3456', False)],
)
async def test_config_kwargs_set(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        experiments3,
        test_uid,
        conf_effective,
):
    experiments3.add_config(
        match={
            'predicate': {
                'type': 'contains',
                'init': {
                    'arg_name': 'yandex_uid',
                    'set_elem_type': 'string',
                    'value': test_uid,
                },
            },
            'enabled': True,
        },
        name='conf3_foo',
        trait_tags=['enable-debug'],
        consumers=['api-proxy/test-handler'],
        clauses=[],
        default_value={'data': 'from config'},
    )
    await taxi_api_proxy.invalidate_caches()

    path = '/path/to/test/handler'
    await endpoints.safely_create_endpoint(
        path=path,
        endpoint_id='test-handler',
        get_handler=load_yaml('test_config_kwargs_set.yaml'),
    )
    response = await taxi_api_proxy.get(
        path,
        headers={'X-Yandex-UID': '12345', 'X-YaTaxi-Bound-Uids': '4444,5555'},
    )
    assert response.status_code == 200
    assert response.json()['effective'] == conf_effective
    if conf_effective:
        assert response.json()['value'] == {'data': 'from config'}

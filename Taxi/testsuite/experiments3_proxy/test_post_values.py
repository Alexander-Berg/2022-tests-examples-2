import pytest


@pytest.mark.parametrize(
    'path,names,modified_stamps',
    [
        ('/v1/configs', ['config1', 'missing', 'config2'], (1, 10)),
        ('/v1/experiments', ['exp1', 'missing', 'exp2'], (2, 20)),
    ],
)
@pytest.mark.config(TVM_ENABLED=False)
def test_post_values(
        taxi_experiments3_proxy,
        mockserver,
        load_json,
        path,
        names,
        modified_stamps,
):
    @mockserver.json_handler('/experiments3-upstream/v1/configs/updates/')
    def configs_upstream(request):
        return load_json('configs.json')

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def exp_upstream(request):
        return load_json('experiments.json')

    taxi_experiments3_proxy.invalidate_caches()
    configs_upstream.wait_call()
    exp_upstream.wait_call()

    body = {'names': names}
    response = taxi_experiments3_proxy.post(path, json=body)
    assert response.status_code == 200
    data = response.json()
    assert len(data['values']) == 2

    for value, name, last_modified in zip(
            data['values'], names, modified_stamps,
    ):
        if name == 'missing':
            assert value['name'] != name
            continue
        assert value['name'] == name
        assert value['last_modified_at'] == last_modified
        assert value['match']['enabled']
        assert value['match']['consumers'] == [{'name': 'consumer'}]


def test_fresh_value(taxi_experiments3_proxy, mockserver, load_json):
    @mockserver.json_handler('/experiments3-upstream/v1/configs/updates/')
    def upstream(request):
        if getattr(upstream, 'first_time', True):
            upstream.first_time = False
            return load_json('configs.json')
        else:
            return load_json('configs2.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    body = {'names': ['config1']}
    response = taxi_experiments3_proxy.post('/v1/configs', json=body)
    assert response.status_code == 200
    data = response.json()
    assert len(data['values']) == 1
    value = data['values'][0]

    assert value['name'] == 'config1'
    assert value['last_modified_at'] == 1
    assert value['match']['predicate']['type'] == 'true'

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    response = taxi_experiments3_proxy.post('/v1/configs', json=body)
    assert response.status_code == 200
    data = response.json()
    assert len(data['values']) == 1
    value = data['values'][0]

    assert value['name'] == 'config1'
    assert value['last_modified_at'] == 5
    assert value['match']['predicate']['type'] == 'false'


@pytest.mark.parametrize(
    'path,names,result_name',
    [
        ('/v1/configs', ['config1', 'config2'], 'config2'),
        ('/v1/experiments', ['exp1', 'exp2'], 'exp2'),
    ],
)
@pytest.mark.config(TVM_ENABLED=False)
def test_newer_than(
        taxi_experiments3_proxy,
        mockserver,
        load_json,
        path,
        names,
        result_name,
):
    @mockserver.json_handler('/experiments3-upstream/v1/configs/updates/')
    def configs_upstream(request):
        return load_json('configs.json')

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def exp_upstream(request):
        return load_json('experiments.json')

    taxi_experiments3_proxy.invalidate_caches()
    configs_upstream.wait_call()
    exp_upstream.wait_call()

    body = {'names': names, 'newer_than': 5}
    response = taxi_experiments3_proxy.post(path, json=body)
    assert response.status_code == 200
    data = response.json()
    assert len(data['values']) == 1

    assert data['values'][0]['name'] == result_name
    assert data['values'][0]['last_modified_at'] > 5

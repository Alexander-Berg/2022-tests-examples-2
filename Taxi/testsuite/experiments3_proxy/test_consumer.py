import pytest


@pytest.mark.parametrize(
    'request_path', ['/v1/configs/updates', '/v1/experiments/updates'],
)
def test_obligatory_consumer(taxi_experiments3_proxy, request_path):
    response = taxi_experiments3_proxy.get(
        request_path, params={'newer_than': -1, 'limit': 100},
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {'error': {'text': 'Param consumer not found'}}


@pytest.mark.parametrize(
    'request_path, my_consumer, other_consumer, array_name',
    [
        ('/v1/configs/updates', 'cfg_specific', 'exp_specific', 'configs'),
        (
            '/v1/experiments/updates',
            'exp_specific',
            'cfg_specific',
            'experiments',
        ),
    ],
)
def test_consumers(
        taxi_experiments3_proxy,
        mockserver,
        load_json,
        request_path,
        my_consumer,
        other_consumer,
        array_name,
):
    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream_exp(request):
        return load_json('experiments.json')

    @mockserver.json_handler('/experiments3-upstream/v1/configs/updates/')
    def upstream_cfg(request):
        return load_json('configs.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream_exp.wait_call()
    upstream_cfg.wait_call()

    response = taxi_experiments3_proxy.get(
        request_path,
        params={'consumer': my_consumer, 'newer_than': -1, 'limit': 100},
    )
    assert response.status_code == 200
    data = response.json()
    assert array_name in data
    assert len(data[array_name]) == 1

    response = taxi_experiments3_proxy.get(
        request_path,
        params={'consumer': other_consumer, 'newer_than': -1, 'limit': 100},
    )
    assert response.status_code == 200
    data = response.json()
    assert array_name in data
    assert len(data[array_name]) == 0


@pytest.mark.parametrize(
    'request_path, array_name',
    [
        ('/v1/configs/updates', 'configs'),
        ('/v1/experiments/updates', 'experiments'),
    ],
)
@pytest.mark.config(EXPERIMENTS3_PROXY_CHECK_CONSUMER=True)
def test_consumer_no_experiments(
        taxi_experiments3_proxy, mockserver, request_path, array_name,
):
    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream_exp(request):
        return {'experiments': []}

    @mockserver.json_handler('/experiments3-upstream/v1/configs/updates/')
    def upstream_cfg(request):
        return {'configs': []}

    @mockserver.json_handler(
        '/experiments3-upstream/v1/experiments/filters/consumers/names/',
    )
    def upstream_consumers(request):
        return {'consumers': [{'name': 'hidden_consumer'}]}

    taxi_experiments3_proxy.invalidate_caches()
    upstream_exp.wait_call()
    upstream_cfg.wait_call()
    upstream_consumers.wait_call()

    response = taxi_experiments3_proxy.get(
        request_path,
        params={'consumer': 'hidden_consumer', 'newer_than': -1, 'limit': 100},
    )

    assert response.status_code == 200
    assert response.json() == {array_name: []}

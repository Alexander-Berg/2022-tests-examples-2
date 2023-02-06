import urllib.parse

import pytest


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=False)
def test_unknown_consumer_nocheck(taxi_experiments3_proxy):
    """Proxy returns empty list of experiments for unknown consumer."""
    response = _request(taxi_experiments3_proxy, 'unknown')
    assert response.status_code == 200
    data = response.json()
    assert data == {'experiments': []}


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=True)
def test_unknown_consumer(taxi_experiments3_proxy):
    """Proxy returns 404 for unknown consumer."""
    response = _request(taxi_experiments3_proxy, 'unknown')
    assert response.status_code == 404
    data = response.json()
    assert data == {'error': {'text': 'consumer not found'}}


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=True)
def test_without_consumers(taxi_experiments3_proxy, mockserver, load_json):
    """Proxy loads experiments without consumers well."""

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream(request):
        return load_json('experiments_without_consumers.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    # Service cannot start if cannot update cache. So 404 Not Found tells us
    # that experiment without consumers is handled as expected.
    response = _request(taxi_experiments3_proxy, 'unknown')
    assert response.status_code == 404


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=False)
@pytest.mark.parametrize(
    'consumer,last_modified_at,enabled',
    [('consumer1', 2, False), ('consumer2', 2, True)],
)
def test_removed_consumer(
        consumer,
        last_modified_at,
        enabled,
        taxi_experiments3_proxy,
        mockserver,
        load_json,
):
    """Removed consumer marked as disabled experiment."""

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream(request):
        return load_json('experiment_with_removed_consumer.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    response = _request(taxi_experiments3_proxy, consumer)
    assert response.status_code == 200
    data = response.json()
    assert data['experiments'][0]['name'] == 'experiment1'
    assert data['experiments'][0]['last_modified_at'] == last_modified_at
    assert data['experiments'][0]['match']['enabled'] == enabled


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=False)
@pytest.mark.parametrize(
    'consumer,exp_lm_enbl',
    [
        # consumer, [(experiment, last_modified_at, enabled), ...]
        ('consumer1', [('experiment1', 3, False)]),
        (
            'consumer2',
            [
                ('experiment2', 2, True),
                ('experiment1', 3, False),
                ('experiment3', 4, True),
            ],
        ),
    ],
)
def test_guarantee_order(
        consumer, exp_lm_enbl, taxi_experiments3_proxy, mockserver, load_json,
):
    """Proxy guarantee experiments are sorted by last_modified_at."""

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream(request):
        return load_json('experiments_enabled_and_disabled.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    response = _request(taxi_experiments3_proxy, consumer)
    assert response.status_code == 200
    data = response.json()
    real = [
        (obj['name'], obj['last_modified_at'], obj['match']['enabled'])
        for obj in data['experiments']
    ]
    assert real == exp_lm_enbl


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=False)
@pytest.mark.parametrize(
    'newer_than,limit,expected_experiments',
    [
        # Total five experiments
        (
            -1,
            100,
            [
                'experiment1',
                'experiment2',
                'experiment3',
                'experiment4',
                'experiment5',
            ],
        ),
        # First is skipped because it version already known to server,
        # two taken
        (1, 2, ['experiment2', 'experiment3']),
    ],
)
def test_limit_offset(
        newer_than,
        limit,
        expected_experiments,
        taxi_experiments3_proxy,
        mockserver,
        load_json,
):
    """Proxy takes limit and offset."""

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream(request):
        return load_json('experiments_for_one_consumer.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    response = _request(
        taxi_experiments3_proxy,
        'consumer1',
        newer_than=newer_than,
        limit=limit,
    )
    assert response.status_code == 200
    data = response.json()
    real = [obj['name'] for obj in data['experiments']]
    assert real == expected_experiments


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=False)
def test_many_experiments(taxi_experiments3_proxy, mockserver):
    start_test = False
    call_count = 0

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream(request):
        nonlocal call_count
        nonlocal start_test
        experiments = []
        if not start_test:
            return {'experiments': experiments}
        if call_count == 0:
            for i in range(100):
                experiments.append(
                    {
                        'name': 'experiment{}'.format(i),
                        'last_modified_at': i,
                        'match': {
                            'enabled': True,
                            'consumers': [{'name': 'consumer1'}],
                        },
                        'clauses': [],
                    },
                )
            call_count = 1
            return {'experiments': experiments}
        elif call_count == 1:
            assert 'newer_than' in request.args
            assert request.args['newer_than'] == '99'
            return {'experiments': experiments}

    start_test = True
    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()
    upstream.wait_call()


def _request(taxi_experiments3_proxy, consumer, newer_than=-1, limit=100):
    response = taxi_experiments3_proxy.get(
        _build_url(consumer, newer_than, limit), headers={},
    )
    return response


def _build_url(consumer, newer_than=-1, limit=100):
    params = {'consumer': consumer, 'newer_than': newer_than, 'limit': limit}
    return '/v1/experiments/updates?%s' % urllib.parse.urlencode(params)

import datetime
import json

import pytest

CACHE_KEY = (
    'cache/'
    'categories:econom;'
    'destination:true;'
    'order_point_geohash:uc4rcfq9fqx;'
    'payment_type:ya_pay;'
    'user_id:some_user_id'
)


@pytest.mark.experiments3(filename='cache_settings_exp.json')
@pytest.mark.experiments3(filename='settings_exp.json')
@pytest.mark.config(ALT_OFFER_DISCOUNT_CANDIDATES_TIMEOUT_REDUCING=3)
@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='long_search/disabled_exp.json')
@pytest.mark.parametrize(
    'testcase',
    [
        'only_econom_candidate',
        'one_chain_candidate',
        'ok_candidates',
        'reposition_candidates',
        'only_chain_candidates',
        'empty_candidates',
    ],
)
async def test_perfect_chain_base(
        taxi_alt_offer_discount, load_json, mockserver, testcase, statistics,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(request):
        request_json = load_json('perfect_chain/candidates_request.json')
        request_json['timeout'] = request_json['timeout'] - 3
        assert request.json == request_json
        return load_json(f'perfect_chain/{testcase}.json')

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        f'perfect_chain/{testcase}_params.json',
    )


@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.experiments3(filename='long_search/disabled_exp.json')
@pytest.mark.parametrize(
    'testcase, exp_values, times',  # 'success' in all other
    [
        (
            'failed_absolute',
            {
                'max_chain_supply_time_s': 600,
                'min_absolute_win_s': 23,
                'min_relative_win': 400,
            },
            {'time1': 400, 'left_time1': 350, 'time2': 500, 'left_time2': 428},
        ),
        (
            'failed_relative',
            {
                'max_chain_supply_time_s': 600,
                'min_absolute_win_s': -1,
                'min_relative_win': 0.66,
            },
            {'time1': 400, 'left_time1': 350, 'time2': 500, 'left_time2': 428},
        ),
        (
            'failed_performer_time',
            {
                'max_chain_supply_time_s': 49,
                'min_absolute_win_s': -1,
                'min_relative_win': 400,
            },
            {'time1': 400, 'left_time1': 350, 'time2': 500, 'left_time2': 428},
        ),
    ],
)
async def test_perfect_trigger(
        taxi_alt_offer_discount,
        taxi_alt_offer_discount_monitor,
        load_json,
        mockserver,
        experiments3,
        mocked_time,
        testcase,
        exp_values,
        times,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(_):
        c_response = load_json(f'perfect_chain/only_chain_candidates.json')
        c_response['candidates'][0]['route_info']['time'] = times['time1']
        c_response['candidates'][1]['route_info']['time'] = times['time2']
        c_response['candidates'][0]['chain_info']['left_time'] = times[
            'left_time1'
        ]
        c_response['candidates'][1]['chain_info']['left_time'] = times[
            'left_time2'
        ]
        return c_response

    exp = load_json('perfect_chain/trigger_exp.json')['configs'][0]
    exp['default_value']['max_chain_supply_time_s'] = exp_values[
        'max_chain_supply_time_s'
    ]
    exp['default_value']['min_absolute_win_s'] = exp_values[
        'min_absolute_win_s'
    ]
    exp['default_value']['min_relative_win'] = exp_values['min_relative_win']
    experiments3.add_config(**exp)

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == {'offers': []}

    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_alt_offer_discount.tests_control(invalidate_caches=False)
    metrics = await taxi_alt_offer_discount_monitor.get_metric(
        'alt_offer_discount_metrics',
    )

    failed = metrics['offer_result']['moscow']['perfect_chain']['failed']

    if testcase == 'failed_absolute':
        assert failed['absolute_win'] == 1
    elif testcase == 'failed_relative':
        assert failed['relative_win'] == 1
    elif testcase == 'failed_performer_time':
        assert failed['performer_time_threshold'] == 1


@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='long_search/disabled_exp.json')
@pytest.mark.parametrize(
    'fallback_name, response_file_name',
    [
        (None, 'perfect_chain/ok_candidates_params.json'),
        ('alt_offer_discount_metrics.moscow.assignment.fallback', None),
        (
            'alt_offer_discount_metrics.spb.assignment.fallback',
            'perfect_chain/ok_candidates_params.json',
        ),
        ('alt_offer_discount_metrics.moscow.processing.fallback', None),
        (
            'alt_offer_discount_metrics.spb.processing.fallback',
            'perfect_chain/ok_candidates_params.json',
        ),
    ],
)
async def test_perfect_chain_fallback_flow(
        taxi_alt_offer_discount,
        load_json,
        mockserver,
        statistics,
        fallback_name,
        response_file_name,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(_):
        return load_json(f'perfect_chain/ok_candidates.json')

    body = load_json('request.json')
    expected_response = (
        {'offers': []}
        if response_file_name is None
        else load_json(response_file_name)
    )
    if fallback_name is not None:
        statistics.fallbacks = [fallback_name]

    await taxi_alt_offer_discount.tests_control(invalidate_caches=True)

    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.mock_order_search(
    'perfect_chain/candidates_request.json',
    'perfect_chain/deviation_candidates.json',
)
async def test_performer_time_deviation(
        taxi_alt_offer_discount, load_json, mockserver, experiments3,
):
    exp = load_json('perfect_chain/enabled_exp.json')['configs'][0]
    exp['default_value']['performer_time_deviation_s'] = 5
    experiments3.add_config(**exp)

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json()['offers'][0]['variables'] == {
        'baseline_supply_time_s': 17.0,
        'chain_supply_time_s': 0.0,
    }


@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.mock_order_search(
    'perfect_chain/candidates_request.json',
    'perfect_chain/min_left_time_candidates.json',
)
async def test_min_left_time(
        taxi_alt_offer_discount, load_json, mockserver, experiments3,
):
    exp = load_json('perfect_chain/enabled_exp.json')['configs'][0]
    exp['default_value']['min_left_time_s'] = 54
    experiments3.add_config(**exp)

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'perfect_chain/min_left_time_candidates_params.json',
    )


@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.mock_order_search(
    'perfect_chain/candidates_request.json',
    'perfect_chain/ok_candidates.json',
)
async def test_perfect_chain_redis_set(
        taxi_alt_offer_discount, redis_store, load_json,
):
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200

    proc_params = json.loads(
        redis_store.get('proc_params:perfect_chain:request_id').decode(
            'utf-8',
        ),
    )
    offer_info = json.loads(
        redis_store.get('offers_info:request_id').decode('utf-8'),
    )
    assert proc_params == {'alt_offer_discount.chain_supply_time_s': 10.0}
    assert offer_info == [
        {'alternative_type': 'perfect_chain', 'info': {'eta': 62}},
    ]


@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.mock_order_search(
    'perfect_chain/candidates_request.json',
    'perfect_chain/ok_candidates.json',
)
@pytest.mark.now('2021-12-27T16:38:00.000000+0000')
async def test_perfect_chain_metrics(
        taxi_alt_offer_discount,
        taxi_alt_offer_discount_monitor,
        load_json,
        mocked_time,
):
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200

    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_alt_offer_discount.tests_control(invalidate_caches=False)
    metrics = await taxi_alt_offer_discount_monitor.get_metric(
        'alt_offer_discount_metrics',
    )

    assert metrics == load_json('perfect_chain/ok_candidates_metrics.json')


@pytest.mark.experiments3(filename='long_search/enabled_exp.json')
@pytest.mark.parametrize(
    'testcase', ['few_candidates', 'ok_candidates', 'empty_candidates'],
)
async def test_long_search_base(
        taxi_alt_offer_discount, load_json, mockserver, testcase,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(request):
        assert request.json == load_json('long_search/candidates_request.json')
        return load_json(f'long_search/{testcase}.json')

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(f'long_search/{testcase}_params.json')


@pytest.mark.mock_order_search(
    'long_search/candidates_request.json', 'long_search/ok_candidates.json',
)
@pytest.mark.experiments3(filename='long_search/enabled_exp.json')
async def test_long_search_redis_set(
        taxi_alt_offer_discount, redis_store, load_json,
):
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200
    params = json.loads(
        redis_store.get('proc_params:perfect_chain:request_id').decode(
            'utf-8',
        ),
    )
    assert params == {'alt_offer_discount.is_long_search': True}


@pytest.mark.mock_order_search(
    'long_search/candidates_request.json', 'long_search/ok_candidates.json',
)
@pytest.mark.experiments3(filename='long_search/enabled_exp.json')
@pytest.mark.now('2021-12-27T16:38:00.000000+0000')
async def test_long_search_metrics(
        taxi_alt_offer_discount,
        taxi_alt_offer_discount_monitor,
        load_json,
        mocked_time,
):
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200

    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_alt_offer_discount.tests_control(invalidate_caches=False)
    metrics = await taxi_alt_offer_discount_monitor.get_metric(
        'alt_offer_discount_metrics',
    )
    assert metrics == load_json('long_search/ok_candidates_metrics.json')


@pytest.mark.parametrize('alt_type', ['perfect_chain', 'long_search'])
@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={'br': [37 - 0.00001, 52 - 0.00001], 'tl': [37 + 0.1, 52 + 0.1]},
    values=[{'x': 0, 'y': 0, 'surge': 1, 'weight': 1.0}],
)
async def test_small_surge(
        taxi_alt_offer_discount,
        load_json,
        alt_type,
        mockserver,
        heatmap_storage_fixture,
        experiments3,
):
    exp = load_json(f'{alt_type}/enabled_exp.json')['configs'][0]
    exp['default_value']['min_surge_value'] = 1.0
    experiments3.add_config(**exp)

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == {'offers': []}


@pytest.mark.parametrize('alt_type', ['perfect_chain', 'long_search'])
@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={'br': [38 - 0.00001, 53 - 0.00001], 'tl': [38 + 0.1, 53 + 0.1]},
    values=[{'x': 0, 'y': 0, 'surge': 2, 'weight': 1.0}],
)
async def test_no_surge(
        taxi_alt_offer_discount,
        load_json,
        alt_type,
        mockserver,
        heatmap_storage_fixture,
        experiments3,
):
    exp = load_json(f'{alt_type}/enabled_exp.json')['configs'][0]
    exp['default_value']['min_surge_value'] = 1.0
    experiments3.add_config(**exp)

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == {'offers': []}


@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.parametrize('alt_type', ['perfect_chain', 'long_search'])
@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={'br': [37 - 0.00001, 52 - 0.00001], 'tl': [37 + 0.1, 52 + 0.1]},
    values=[{'x': 0, 'y': 0, 'surge': 2, 'weight': 1.0}],
)
async def test_big_surge(
        taxi_alt_offer_discount,
        load_json,
        alt_type,
        mockserver,
        heatmap_storage_fixture,
        experiments3,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(request):
        assert request.json == load_json(f'{alt_type}/candidates_request.json')
        return load_json(f'{alt_type}/ok_candidates.json')

    exp = load_json(f'{alt_type}/enabled_exp.json')['configs'][0]
    exp['default_value']['min_surge_value'] = 1.0
    experiments3.add_config(**exp)

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        f'{alt_type}/ok_candidates_params.json',
    )


@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.experiments3(filename='add_order_id_exp.json')
async def test_add_order_id(taxi_alt_offer_discount, load_json, mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(request):
        request_json = load_json('perfect_chain/candidates_request.json')
        request_json['order_id'] = 'alt_offer_discount_pricing/request_id'
        assert request.json == request_json
        return load_json(f'perfect_chain/ok_candidates.json')

    body = load_json('request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'perfect_chain/ok_candidates_params.json',
    )


@pytest.mark.mock_order_search(
    'long_search/candidates_request.json', 'long_search/ok_candidates.json',
)
@pytest.mark.experiments3(filename='long_search/enabled_exp.json')
async def test_pricing_and_processing(taxi_alt_offer_discount, load_json):
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200

    body = load_json('order_proc_request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/order-proc-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == {'alt_offer_discount.is_long_search': True}


@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.mock_order_search(
    'perfect_chain/candidates_request.json',
    'perfect_chain/offers_info_candidates.json',
)
async def test_pricing_and_offer_info(taxi_alt_offer_discount, load_json):
    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200

    body = {
        'request_id': 'request_id',
        'alternatives': [{'type': 'perfect_chain'}],
    }
    response = await taxi_alt_offer_discount.post('/v1/offers-info', json=body)
    assert response.status_code == 200
    assert response.json() == {
        'offers_info': [
            {'alternative_type': 'perfect_chain', 'info': {'eta': 74}},
        ],
    }


@pytest.mark.parametrize('alt_type', ['perfect_chain', 'long_search'])
@pytest.mark.now('2022-06-23T00:00:00.000000+0000')
@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='cache_settings_exp.json')
async def test_save_cache(
        taxi_alt_offer_discount,
        taxi_alt_offer_discount_monitor,
        redis_store,
        load_json,
        alt_type,
        mockserver,
        experiments3,
        mocked_time,
):
    exp = load_json(f'{alt_type}/enabled_exp.json')['configs'][0]
    experiments3.add_config(**exp)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(_):
        return load_json(f'{alt_type}/ok_candidates.json')

    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        f'{alt_type}/ok_candidates_params.json',
    )

    cache_data = json.loads(redis_store.get(CACHE_KEY).decode('utf-8'))

    assert cache_data == load_json(f'{alt_type}/cache_data.json')

    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_alt_offer_discount.tests_control(invalidate_caches=False)
    metrics = await taxi_alt_offer_discount_monitor.get_metric(
        'alt_offer_discount_metrics',
    )

    assert metrics['cache']['saved'] == 1


@pytest.mark.parametrize('alt_type', ['perfect_chain', 'long_search'])
@pytest.mark.now('2022-06-23T00:00:00.000000+0000')
@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='cache_settings_exp.json')
async def test_cache_usage(
        taxi_alt_offer_discount,
        taxi_alt_offer_discount_monitor,
        redis_store,
        load_json,
        alt_type,
        experiments3,
        mocked_time,
):
    exp = load_json(f'{alt_type}/enabled_exp.json')['configs'][0]
    experiments3.add_config(**exp)

    cache_data = load_json(f'{alt_type}/cache_data.json')
    cache_data['request_id'] = 'other'
    redis_store.set(CACHE_KEY, json.dumps(cache_data))

    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        f'{alt_type}/ok_candidates_params.json',
    )

    new_cache_data = json.loads(redis_store.get(CACHE_KEY).decode('utf-8'))
    # checking that cache has not been updated
    assert cache_data == new_cache_data

    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_alt_offer_discount.tests_control(invalidate_caches=False)
    metrics = await taxi_alt_offer_discount_monitor.get_metric(
        'alt_offer_discount_metrics',
    )

    assert metrics['cache']['hit'] == 1


@pytest.mark.now('2022-06-23T00:00:00.000000+0000')
@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='cache_settings_exp.json')
@pytest.mark.mock_order_search(
    'perfect_chain/candidates_request.json',
    'perfect_chain/empty_candidates.json',
)
async def test_cache_read_disabled(
        taxi_alt_offer_discount, redis_store, load_json, experiments3,
):
    exp = load_json('cache_settings_exp.json')['configs'][0]
    exp['default_value']['read_enabled'] = False
    experiments3.add_config(**exp)

    cache_data = load_json('perfect_chain/cache_data.json')
    cache_data['request_id'] = 'other'
    redis_store.set(CACHE_KEY, json.dumps(cache_data))

    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200
    assert response.json() == {'offers': []}

    new_cache_data = json.loads(redis_store.get(CACHE_KEY).decode('utf-8'))

    assert cache_data != new_cache_data


@pytest.mark.now('2022-06-23T00:00:00.000000+0000')
@pytest.mark.experiments3(filename='perfect_chain/enabled_exp.json')
@pytest.mark.experiments3(filename='perfect_chain/trigger_exp.json')
@pytest.mark.experiments3(filename='cache_settings_exp.json')
@pytest.mark.mock_order_search(
    'perfect_chain/candidates_request.json',
    'perfect_chain/empty_candidates.json',
)
async def test_cache_write_disabled(
        taxi_alt_offer_discount, redis_store, load_json, experiments3,
):
    exp = load_json('cache_settings_exp.json')['configs'][0]
    exp['default_value']['write_enabled'] = False
    experiments3.add_config(**exp)

    response = await taxi_alt_offer_discount.post(
        '/v1/pricing-params', json=load_json('request.json'),
    )
    assert response.status_code == 200
    assert response.json() == {'offers': []}

    assert redis_store.get(CACHE_KEY) is None

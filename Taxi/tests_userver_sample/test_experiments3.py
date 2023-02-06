import pytest


@pytest.mark.experiments3(filename='consumer1_v1.json')
async def test_exp3_simple(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 1},
        ],
    }


@pytest.mark.parametrize('param, expected_status', [('abc', 200), (None, 500)])
async def test_exp3_required_arg(taxi_userver_sample, param, expected_status):
    response = await taxi_userver_sample.post(
        'experiments3', json={'required_user_id': param},
    )
    assert response.status_code == expected_status
    if expected_status == 500:
        assert response.json()['message'] == (
            'Missing mandatory key required_user_id '
            'for kwarg builder TestRequired'
        )


@pytest.mark.experiments3(filename='consumer1_v1.json')
async def test_exp3_cache_update_ver_inc(
        taxi_userver_sample, experiments3, load_json,
):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 1},
        ],
    }

    experiments3.add_experiments_json(load_json('consumer1_v2.json'))

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 10000, 'version': 2},
        ],
    }


@pytest.mark.experiments3(filename='consumer1_v2.json')
async def test_exp3_cache_update_ver_dec(
        taxi_userver_sample, experiments3, load_json,
):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 10000, 'version': 2},
        ],
    }

    experiments3.add_experiments_json(load_json('consumer1_v1.json'))

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 10000, 'version': 2},
        ],
    }


@pytest.mark.experiments3(filename='consumer1_v1.json')
async def test_exp3_doesnt_match(taxi_userver_sample, experiments3, load_json):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_doesnt_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 1},
        ],
    }

    experiments3.add_experiments_json(load_json('consumer1_v2.json'))

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_doesnt_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {'configs': [], 'experiments': []}


@pytest.mark.experiments3(filename='consumer1_v1.json')
async def test_exp3_clauses(taxi_userver_sample, experiments3, load_json):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 1},
        ],
    }

    experiments3.add_experiments_json(load_json('consumer1_v3.json'))

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 1, 'value': 20000, 'version': 3},
        ],
    }


@pytest.mark.experiments3(filename='consumer1_v1_multiple_experiments.json')
async def test_exp3_multiple_experiments(
        taxi_userver_sample, experiments3, load_json,
):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    experiments = response.json()['experiments']
    assert sorted(experiments, key=lambda i: i['name']) == [
        {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 1},
        {'name': 'exp2', 'position': 0, 'value': 9875, 'version': 3},
    ]

    experiments3.add_experiments_json(
        load_json('consumer1_v2_multiple_experiments.json'),
    )

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    experiments = response.json()['experiments']
    assert sorted(experiments, key=lambda i: i['name']) == [
        {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 5},
        {'name': 'exp2', 'position': 0, 'value': 9875, 'version': 4},
    ]


@pytest.mark.experiments3(filename='consumer1_v1.json')
async def test_exp3_user_agent(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={'phone_id': 'phone_id', 'user_id': 'user_id'},
        headers={
            'User-Agent': (
                'ru.yandex.ytaxi/4.03.11463 (iPhone; '
                'iPhone5,2; iOS 10.3.3; Darwin)'
            ),
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 1},
        ],
    }

    response = await taxi_userver_sample.post(
        'experiments3',
        json={'phone_id': 'phone_id', 'user_id': 'user_id'},
        headers={
            'User-Agent': (
                'ru.yandex.ytaxi/10.03.11463 (iPhone; '
                'iPhone5,2; iOS 10.3.3; Darwin)'
            ),
        },
        params={'consumer': 'consumer1'},
    )

    assert response.status_code == 200
    assert response.json() == {'configs': [], 'experiments': []}


@pytest.mark.experiments3(filename='consumer1_polygon.json')
async def test_exp3_falls_inside_polygon(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id',
            'user_id': 'user_id',
            'point_a': [37.04910393749999, 55.864550814117806],
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [],
        'experiments': [
            {'name': 'exp1', 'position': 0, 'value': 9875, 'version': 1},
        ],
    }

    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id',
            'user_id': 'user_id',
            'point_a': [37.26745720898437, 55.897743713698766],
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {'configs': [], 'experiments': []}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.tvm2_ticket({2015022: 'MYTICKET'})
async def test_exp3_tvm(taxi_userver_sample, mockserver):
    await taxi_userver_sample.invalidate_caches(clean_update=False)
    # pylint: disable=unused-variable
    @mockserver.json_handler('/v1/experiments/updates')
    def handler(request):
        assert request.headers['X-Ya-Service-Ticket'] == 'MYTICKET'
        return {'experiments': []}

    # pylint: disable=unused-variable
    @mockserver.json_handler('/v1/configs/updates')
    def handler_config(request):
        assert request.headers['X-Ya-Service-Ticket'] == 'MYTICKET'
        return {'configs': []}

    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id',
            'user_id': 'user_id',
            'point_a': [37.04910393749999, 55.864550814117806],
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {'configs': [], 'experiments': []}


async def test_exp3_consumers_by_prefix(
        taxi_userver_sample, experiments3, load_json,
):
    experiments3.add_experiments_json(load_json('exp1.json'))
    await taxi_userver_sample.invalidate_caches(clean_update=False)
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'prefix1_consumer1'},
    )
    assert response.status_code == 200
    experiments = response.json()['experiments']
    assert sorted(experiments, key=lambda i: i['name']) == [
        {
            'name': 'exp1',
            'position': 0,
            'value': 9875,
            'version': 1,
            'alias': 'some_other_clause',
        },
    ]

    experiments3.add_experiments_json(load_json('exp2.json'))
    await taxi_userver_sample.invalidate_caches(clean_update=False)
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'prefix2_consumer2'},
    )
    assert response.status_code == 200
    experiments = response.json()['experiments']
    assert sorted(experiments, key=lambda i: i['name']) == [
        {'name': 'exp2', 'position': 0, 'value': 9875, 'version': 1},
    ]

    await taxi_userver_sample.invalidate_caches(clean_update=False)
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'prefix3_consumer1'},
    )
    assert response.status_code == 200
    experiments = response.json()['experiments']
    assert sorted(experiments, key=lambda i: i['name']) == []

    experiments3.add_experiments_json(load_json('exp3.json'))
    await taxi_userver_sample.invalidate_caches(clean_update=False)
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'prefix1_consumer3'},
    )
    assert response.status_code == 200
    experiments = response.json()['experiments']
    assert sorted(experiments, key=lambda i: i['name']) == [
        {'name': 'exp3', 'position': 0, 'value': 9875, 'version': 1},
    ]

    await taxi_userver_sample.invalidate_caches(clean_update=False)
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id_match',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    experiments = response.json()['experiments']
    assert sorted(experiments, key=lambda i: i['name']) == [
        {'name': 'exp3', 'position': 0, 'value': 9875, 'version': 1},
    ]


@pytest.mark.experiments3(filename='consumer1_round_up.json')
async def test_exp3_round_up(taxi_userver_sample):
    async def get_clause(timestamp: int):
        response = await taxi_userver_sample.post(
            'experiments3',
            json={
                'application': 'iphone',
                'version': '1.1.1',
                'user_id': 'user_id',
                'timestamp': timestamp,
            },
            params={'consumer': 'consumer1'},
        )
        assert response.status_code == 200
        return response.json()['experiments'][0]['position']

    clause0 = await get_clause(timestamp=0)
    for timestamp in range(1, 10):
        assert clause0 == await get_clause(timestamp)

    clause1 = await get_clause(timestamp=10)
    for timestamp in range(11, 20):
        assert clause1 == await get_clause(timestamp)


@pytest.mark.experiments3(filename='configs.json')
async def test_exp3_configs(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'experiments3',
        json={
            'application': 'iphone',
            'version': '1.1.1',
            'phone_id': 'phone_id',
            'user_id': 'user_id',
        },
        params={'consumer': 'consumer1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'configs': [
            {
                'name': 'exp1',
                'position': 0,
                'value': 9875,
                'version': 1,
                'alias': 'some_clause',
            },
        ],
        'experiments': [],
    }

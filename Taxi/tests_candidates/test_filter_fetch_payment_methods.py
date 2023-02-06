import pytest


async def test_onlycard(taxi_candidates):
    request_body = {
        'driver_ids': ['dbid0_uuid0', 'dbid1_uuid3'],
        'zone_id': 'moscow',
        'data_keys': ['payment_methods'],
        'order': {'request': {'surge_price': 1}},
    }

    # dbid1 park doesn't support cash or card
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert drivers[0]['payment_methods'] == ['cash']
    assert set(drivers[1]['payment_methods']) == {'card', 'corp', 'coupon'}


async def test_onlycard_car(taxi_candidates, mongodb):
    mongodb.dbcars.update({'_id': '0'}, {'$set': {'onlycard': True}})
    request_body = {
        'driver_ids': ['dbid0_uuid0'],
        'zone_id': 'moscow',
        'data_keys': ['payment_methods'],
        'order': {'request': {'surge_price': 1}},
    }

    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert set(drivers[0]['payment_methods']) == {'card', 'corp', 'coupon'}


@pytest.mark.parametrize(
    'balance,balance_limit,is_onlycard',
    [
        (0, 10, True),
        (10, 10, False),
        (10, 5, False),
        (-200, 0, False),
        (None, None, False),
        (10, None, False),
        (None, 10, True),
    ],
)
async def test_onlycard_balance(
        taxi_candidates, mongodb, balance, balance_limit, is_onlycard,
):
    mongodb.dbdrivers.update(
        {'_id': 'clid0_uuid0'},
        {'$set': {'balance': balance, 'balance_limit': balance_limit}},
    )
    request_body = {
        'driver_ids': ['dbid0_uuid0'],
        'zone_id': 'moscow',
        'data_keys': ['payment_methods'],
        'order': {'request': {'surge_price': 1}},
    }

    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    if is_onlycard:
        assert set(drivers[0]['payment_methods']) == {'card', 'corp', 'coupon'}
    else:
        assert drivers[0]['payment_methods'] == ['cash']


@pytest.mark.parametrize(
    'allow_onlycard,is_onlycard',
    [(True, True), (False, False), (None, False)],
)
async def test_onlycard_country(
        taxi_candidates, mockserver, mongodb, allow_onlycard, is_onlycard,
):
    mongodb.dbcars.update({'_id': '0'}, {'$set': {'onlycard': True}})

    @mockserver.json_handler('/territories/v1/countries/list')
    def _mock_countries_list(request):
        json = {
            'countries': [
                {
                    '_id': 'rus',
                    'allow_onlycard': allow_onlycard,
                    'code2': 'RU',
                    'name': 'Россия',
                    'phone_code': '7',
                    'phone_max_length': 12,
                    'phone_min_length': 11,
                    'region_id': 225,
                    'updated': '2019-04-23T15:32:48+0000',
                    'national_access_code': '8',
                },
            ],
        }
        return json

    request_body = {
        'driver_ids': ['dbid0_uuid0'],
        'zone_id': 'moscow',
        'data_keys': ['payment_methods'],
        'order': {'request': {'surge_price': 1}},
    }

    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    if is_onlycard:
        assert set(drivers[0]['payment_methods']) == {'card', 'corp', 'coupon'}
    else:
        assert drivers[0]['payment_methods'] == ['cash']

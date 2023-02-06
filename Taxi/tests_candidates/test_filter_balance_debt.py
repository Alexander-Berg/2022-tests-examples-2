import pytest


@pytest.mark.parametrize(
    'balance,balance_limit,deny_onlycard,blocked',
    [
        (20, 0, True, False),
        (10, 10, True, False),
        (-200, 0, True, False),
        (5, 10, False, False),
        (5, 10, None, False),
        (5, 10, True, True),
        (None, None, None, False),
        (10, None, True, False),
        (None, 10, None, False),
        (None, 10, False, False),
        (None, 10, True, True),
    ],
)
async def test_onlycard_balance(
        taxi_candidates,
        driver_positions,
        mongodb,
        balance,
        balance_limit,
        deny_onlycard,
        blocked,
):
    mongodb.dbdrivers.update(
        {'_id': 'clid0_uuid0'},
        {
            '$set': {
                'balance': balance,
                'balance_limit': balance_limit,
                'balance_deny_onlycard': deny_onlycard,
            },
        },
    )
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/balance_debt'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    if blocked:
        assert not drivers
    else:
        assert len(drivers) == 1


@pytest.mark.parametrize(
    'enable,city,country,blocked',
    [
        (True, ['Москва'], ['rus'], False),
        (True, ['none'], ['rus'], False),
        (True, ['Москва'], ['none'], False),
        (True, [], ['rus'], False),
        (True, ['Москва'], [], False),
        (True, [], [], False),
        (True, ['none'], ['none'], True),
        (False, [], [], True),
    ],
)
async def test_onlycard_config(
        taxi_candidates,
        driver_positions,
        mongodb,
        taxi_config,
        enable,
        city,
        country,
        blocked,
):
    taxi_config.set_values(
        dict(
            TAXIMETER_LOW_BALANCE_ONLYCARD={
                'enable': enable,
                'cities': city,
                'countries': country,
            },
        ),
    )
    mongodb.dbdrivers.update(
        {'_id': 'clid0_uuid0'}, {'$set': {'balance_limit': 5}},
    )
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/balance_debt'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    if blocked:
        assert not drivers
    else:
        assert len(drivers) == 1

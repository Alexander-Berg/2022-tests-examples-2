import pytest


@pytest.mark.parametrize(
    'payment_method,expected_uuids',
    [('cash', ['uuid0']), ('card', ['uuid3'])],
)
async def test_filter(
        taxi_candidates, driver_positions, payment_method, expected_uuids,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/payment_method'],
        'point': [55, 35],
        'payment_method': payment_method,
        'zone_id': 'moscow',
        'order': {'request': {'surge_price': 1}},
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    uuids = [dr['uuid'] for dr in drivers]
    assert uuids == expected_uuids


@pytest.mark.config(
    DRIVER_PAYMENT_TYPE_MAPPING={
        'agent': 'online',
        'applepay': 'online',
        'card': 'online',
        'cash': 'cash',
        'coop_account': 'online',
        'corp': 'online',
        'coupon': 'cash',
        'creditcard': 'online',
        'googlepay': 'online',
        'personal_wallet': 'online',
        'yandex_card': 'online',
    },
)
@pytest.mark.experiments3(
    **{
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'name': 'partner_payment_types',
        'consumers': ['candidates/user'],
        'default_value': {'enabled': True, 'use_new_filter': True},
        'is_config': False,
    },
)
@pytest.mark.parametrize(
    'payment_method,expected_uuids', [('cash', ['uuid0']), ('card', [])],
)
async def test_filter_v2(
        mongodb,
        taxi_candidates,
        driver_positions,
        payment_method,
        expected_uuids,
):
    mongodb.tariff_settings.update(
        {'hz': 'moscow'},
        {'$set': {'payment_options': ['card', 'coupon', 'corp', 'cash']}},
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/payment_method'],
        'point': [55, 35],
        'payment_method': payment_method,
        'zone_id': 'moscow',
        'order': {'request': {'surge_price': 1}},
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    uuids = [dr['uuid'] for dr in drivers]
    assert uuids == expected_uuids


@pytest.mark.config(
    CANDIDATES_SKIP_PAYMENT_METHOD_BY_CORP={
        '__default__': [],
        'corp_id': ['dbid0', 'dbid1'],
    },
)
@pytest.mark.parametrize('payment_method', ['cash', 'card'])
async def test_skip_by_corp(taxi_candidates, driver_positions, payment_method):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/payment_method'],
        'point': [55, 35],
        'payment_method': payment_method,
        'zone_id': 'moscow',
        'order': {
            'request': {'surge_price': 1, 'corp': {'client_id': 'corp_id'}},
        },
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    uuids = {dr['uuid'] for dr in drivers}
    expected_uuids = {'uuid0', 'uuid3'}
    assert expected_uuids == uuids

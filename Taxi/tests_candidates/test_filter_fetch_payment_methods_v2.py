import pytest


EXPERIMENT = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'partner_payment_types',
    'consumers': ['candidates/user'],
    'default_value': {'enabled': True, 'use_new_filter': True},
    'is_config': False,
}


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
@pytest.mark.experiments3(**EXPERIMENT)
@pytest.mark.parametrize(
    'driver_id,zone_id,surge_price,payment_methods',
    [
        pytest.param('parkAll_uuid0', 'moscow', 1, {'cash'}, id='wants-cash'),
        pytest.param(
            'parkAll_uuid2',
            'moscow',
            1,
            {'card', 'coupon', 'corp'},
            id='wants-online',
        ),
        pytest.param(
            'parkAll_uuid0',
            'zone_card_coupon_corp',
            1,
            set(),
            id='wants-cash-no-cash-in-zone',
        ),
        pytest.param(
            'parkCardCouponCorp_uuid1',
            'moscow',
            1,
            set(),
            id='wants-cash-no-cash-in-park',
        ),
        pytest.param(
            'parkCardCoupon_uuid3',
            'moscow',
            1,
            {'card', 'coupon'},
            id='wants-online-card-coupon',
        ),
        pytest.param(
            'parkCardCoupon_uuid4',
            'moscow',
            1,
            {'card'},
            id='wants-cash-low-balance',
        ),
        pytest.param(
            'parkAll_uuid0', 'moscow', 1.5, {'cash'}, id='wants-cash-surge',
        ),
        pytest.param(
            'parkAll_uuid7', 'moscow', 1, {'cash'}, id='max-enabled-count',
        ),
        pytest.param(
            'parkAll_uuid8',
            'moscow',
            1,
            {'cash', 'card', 'corp', 'coupon'},
            id='no-payment-type-chosen',
        ),
        pytest.param(
            'parkDeact_uuid5', 'moscow', 1, set(), id='park-deactivated',
        ),
        pytest.param(
            'parkNone_uuid6', 'moscow', 1, set(), id='park-empty-activation',
        ),
        pytest.param(
            'parkAll_uuid0', 'zone_none', 1, set(), id='zone-no-options',
        ),
        pytest.param(
            'parkCardCoupon_uuid4',
            'zone_cash_corp',
            1,
            set(),
            id='park-zone-resulting-none',
        ),
        pytest.param(
            'parkItaly_uuid9',
            'madrid',
            1,
            set(),
            id='country-onlycard-wants-cash',
        ),
        pytest.param(
            'parkItaly_uuid10',
            'madrid',
            1,
            {'card', 'corp', 'coupon'},
            id='country-onlycard-wants-online',
        ),
        pytest.param(
            'parkItaly_uuid11',
            'madrid',
            1,
            {'cash', 'card', 'corp', 'coupon'},
            id='country-onlycard-car-notonlycard-all',
        ),
        pytest.param(
            'parkItalyCashCorp_uuid13',
            'madrid',
            1,
            {'corp'},
            id='country-onlycard-car-corp',
        ),
    ],
)
async def test_driver(
        taxi_candidates, driver_id, zone_id, surge_price, payment_methods,
):
    request_body = {
        'driver_ids': [driver_id],
        'zone_id': zone_id,
        'data_keys': ['payment_methods'],
        'order': {'request': {'surge_price': surge_price}},
    }

    # dbid1 park doesn't support cash or card
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert set(drivers[0]['payment_methods']) == payment_methods

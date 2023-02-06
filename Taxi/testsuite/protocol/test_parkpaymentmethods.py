import pytest


API_OVER_DATA_WORK_MODE = {
    '__default__': {'__default__': 'oldway'},
    'parks-activation-client': {'protocol': 'newway'},
}


def test_parkpaymentmethods(taxi_protocol, db):
    response = taxi_protocol.get(
        '/taximeter/park-payment-methods',
        params={'clid': '999011', 'lat': '55.733863', 'lon': '37.590533'},
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content == {
        'available_methods': {
            'cash': False,
            'card': True,
            'corp': False,
            # applepay & googlepay restricted by zone tariff settings
            'applepay': False,
            'googlepay': False,
            'personal_wallet': False,
            'coop_account': False,
            'coupon': True,
        },
    }


@pytest.mark.parks_activation(
    [
        {
            'park_id': '999011',
            'city_id': 'Москва',
            'revision': 1,
            'last_modified': '1970-01-15T03:56:07.000',
            'data': {
                'deactivated': False,
                'can_cash': True,
                'can_card': False,
                'can_coupon': True,
                'can_corp': False,
                'can_subsidy': False,
            },
        },
    ],
)
@pytest.mark.config(API_OVER_DATA_WORK_MODE=API_OVER_DATA_WORK_MODE)
def test_parkpaymentmethods_parkactivation(taxi_protocol):
    response = taxi_protocol.get(
        '/taximeter/park-payment-methods',
        params={'clid': '999011', 'lat': '0', 'lon': '0'},
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content == {
        'available_methods': {
            'cash': True,
            'card': False,
            'corp': False,
            'applepay': False,
            'googlepay': False,
            'personal_wallet': False,
            'coop_account': False,
            'coupon': True,
        },
    }


def test_corp_parkpaymentmethods(taxi_protocol, db):
    response = taxi_protocol.get(
        '/taximeter/park-payment-methods',
        params={'clid': '999013', 'lat': '55.733863', 'lon': '37.590533'},
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content == {
        'available_methods': {
            'cash': False,
            'card': True,
            'corp': True,
            'applepay': False,
            'googlepay': False,
            'personal_wallet': False,
            'coop_account': False,
            'coupon': True,
        },
    }


def test_corp_parkpaymentmethods_inactive_vats(taxi_protocol, db):
    response = taxi_protocol.get(
        '/taximeter/park-payment-methods',
        params={'clid': '999015', 'lat': '55.733863', 'lon': '37.590533'},
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content == {
        'available_methods': {
            'cash': False,
            'card': True,
            'corp': False,
            'applepay': False,
            'googlepay': False,
            'personal_wallet': False,
            'coop_account': False,
            'coupon': True,
        },
    }


def test_invalid_coords(taxi_protocol, db):
    response = taxi_protocol.get(
        '/taximeter/park-payment-methods',
        params={'clid': '999011', 'lat': '0', 'lon': '0'},
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content == {
        'available_methods': {
            'cash': True,
            'card': True,
            'corp': False,
            'applepay': True,
            'googlepay': True,
            'personal_wallet': True,
            'coop_account': True,
            'coupon': True,
        },
    }

import pytest

URL = '/v1/integration/availability'

DEFAULT_PAYLOAD = {'point': [37.62, 55.75], 'category': 'econom'}


async def test_simple(taxi_payment_methods):
    response = await taxi_payment_methods.post(URL, json=DEFAULT_PAYLOAD)
    assert response.status_code == 200
    assert response.json() == {
        'availability_map': {
            'card': {'in_category': True, 'in_zone': True},
            'cash': {'in_category': True, 'in_zone': True},
            'corp': {'in_category': True, 'in_zone': True},
        },
        'localized_cash_label': 'Наличные',
    }


async def test_zone_not_found(taxi_payment_methods):
    payload = {**DEFAULT_PAYLOAD, 'point': [0.0, 0.0]}
    response = await taxi_payment_methods.post(URL, json=payload)
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'zone not found'}


@pytest.mark.parametrize(
    'accept_language, expected_label',
    [
        pytest.param('en-EN;q=1', 'Cash', id='Eng locale'),
        pytest.param(None, 'Наличные', id='No locale, fallback label'),
    ],
)
async def test_localization(
        taxi_payment_methods, accept_language, expected_label,
):
    response = await taxi_payment_methods.post(
        URL,
        json=DEFAULT_PAYLOAD,
        headers={'Accept-Language': accept_language},
    )
    assert response.status_code == 200
    assert response.json()['localized_cash_label'] == expected_label

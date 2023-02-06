import pytest


@pytest.mark.parametrize(
    'offer_id, expected, expected_code',
    [
        (
            'offer_1',
            {
                'categories': {
                    'business': {
                        'is_fixed_price': True,
                        'payment_type': 'cash',
                        'surge': 1.1,
                        'user_price': 229.0,
                    },
                    'maybach': {
                        'is_fixed_price': True,
                        'payment_type': 'cash',
                        'surge': 1.0,
                        'user_price': 1799.0,
                    },
                    'vip': {
                        'is_fixed_price': True,
                        'payment_type': 'cash',
                        'surge': 1.0,
                        'user_price': 417.0,
                    },
                },
                'common': {
                    'created': '2022-01-15T12:07:15.470004+00:00',
                    'due': '2022-01-15T12:07:15.289561+00:00',
                    'has_fixed_price': True,
                    'id': 'offer_1',
                    'has_decoupling': False,
                    'payment_type': 'cash',
                    'tariff_name': 'moscow',
                    'waypoints_count': 2,
                },
            },
            200,
        ),
        ('offer_2', None, 404),
    ],
    ids=['ok', 'not_found'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['yql_loads.sql'])
async def test_v1_offers_loaded_get(
        taxi_pricing_admin, offer_id, expected_code, expected,
):
    response = await taxi_pricing_admin.get(
        'v1/offers/loaded', params={'offer_id': offer_id},
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        data = response.json()
        assert data == expected

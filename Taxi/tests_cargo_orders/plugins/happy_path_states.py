import pytest


PARK_NAME = 'some park name'
PARK_ORG_NAME = 'some park org name'
PARK_ID = '456'


@pytest.fixture(name='happy_path_park_list')
def _happy_path_park_list(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def handler(request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': PARK_NAME,
                    'org_name': PARK_ORG_NAME,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    return handler


@pytest.fixture(name='happy_path_calc_price_handler')
async def _happy_path_calc_price_handler(
        taxi_cargo_orders, mock_cargo_pricing_calc,
):
    await taxi_cargo_orders.post(
        '/v1/calc-price',
        json={
            'user_id': 'mock-user',
            'order_id': 'taxi-order',
            'cargo_ref_id': 'mock-claim',
            'tariff_class': 'mock-tariff',
            'status': 'finished',
            'taxi_status': 'complete',
            'driver_id': 'mock-driver',
            'source_type': 'presetcar',
        },
    )

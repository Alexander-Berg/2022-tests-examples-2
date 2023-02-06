from testsuite.utils import http

from fleet_rent.entities import car
from fleet_rent.generated.web import web_context as context_module


async def test_car_info_service(
        web_context: context_module.Context, mock_fleet_vehicles,
):
    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    async def _retrieve(request: http.Request):
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'park_id_car_id',
                    'data': {
                        'model': 'model',
                        'brand': 'brand',
                        'number': 'number',
                        'color': 'Желтый',
                        'year': '2525',
                    },
                },
            ],
        }

    car_data = await web_context.external_access.car.get_car_info(
        park_id='park_id', car_id='car_id',
    )

    assert car_data == car.Car(
        park_id='park_id',
        id='car_id',
        model='model',
        brand='brand',
        number='number',
        color='Желтый',
        year=2525,  # If man is still alive...
    )


async def test_try_get_car_into(
        web_context: context_module.Context, mock_fleet_vehicles,
):
    @mock_fleet_vehicles('/v1/vehicles/cache-retrieve')
    async def _retrieve(request: http.Request):
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'park_id_car_id',
                    'data': {
                        'car_id': 'car_id',
                        'model': 'model',
                        'brand': 'brand',
                        'number': 'number',
                        'color': 'Желтый',
                        'year': 2525,
                    },
                },
            ],
        }

    car_data = await web_context.external_access.car.try_get_car_info(
        park_id='park_id', car_id='car_id',
    )

    assert car_data == car.Car(
        park_id='park_id',
        id='car_id',
        model='model',
        brand='brand',
        number='number',
        color='Желтый',
        year=2525,  # If man is still alive...
    )


async def test_try_get_car_into_fail(
        web_context: context_module.Context, mock_fleet_vehicles,
):
    @mock_fleet_vehicles('/v1/vehicles/cache-retrieve')
    async def _retrieve(request: http.Request):
        return {'vehicles': [{'park_id_car_id': 'park_id_car_id'}]}

    car_data = await web_context.external_access.car.try_get_car_info(
        park_id='park_id', car_id='car_id',
    )

    assert car_data is None

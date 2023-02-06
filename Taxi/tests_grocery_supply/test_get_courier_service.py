import pytest

from tests_grocery_supply import models


def make_courier_service(courier_service_dict, pg_db) -> models.CourierService:
    return models.CourierService(
        courier_service_id=courier_service_dict['courier_service_id'],
        name=courier_service_dict['name'],
        address=courier_service_dict['address'],
        ogrn=courier_service_dict['ogrn'],
        work_schedule=courier_service_dict['work_schedule'],
        inn=courier_service_dict['tin'],
        vat=courier_service_dict['vat'],
        pg_db=pg_db['grocery_supply'],
    )


COURIER_SERVICE = {
    'courier_service_id': 1453,
    'name': 'Yandex',
    'address': '123 street',
    'ogrn': '12345',
    'work_schedule': '8:00-19:00',
    'tin': '1234',
    'vat': 20,
}


@pytest.mark.pgsql('grocery_supply')
async def test_basic(taxi_grocery_supply, pgsql):
    courier_service_model = make_courier_service(COURIER_SERVICE, pgsql)

    response = await taxi_grocery_supply.post(
        '/internal/v1/supply/v1/courier-service/info',
        json={
            'courier_service_id': str(
                courier_service_model.courier_service_id,
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()
    courier_service = body['courier_service']
    assert (
        courier_service['courier_service_id']
        == courier_service_model.courier_service_id
    )
    assert courier_service['name'] == courier_service_model.name
    assert courier_service['address'] == courier_service_model.address
    assert courier_service['ogrn'] == courier_service_model.ogrn
    assert (
        courier_service['work_schedule'] == courier_service_model.work_schedule
    )
    assert courier_service['tin'] == courier_service_model.inn
    assert courier_service['vat'] == courier_service_model.vat


async def test_courier_not_found(taxi_grocery_supply):
    response = await taxi_grocery_supply.post(
        '/internal/v1/supply/v1/courier-service/info',
        json={'courier_service_id': '1337'},
    )

    assert response.status_code == 404

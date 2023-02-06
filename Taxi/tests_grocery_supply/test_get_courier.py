import pytest

from tests_grocery_supply import models


def make_courier(courier_dict, pg_db) -> models.Courier:
    courier_service = None
    if courier_dict['courier_service'] is not None:
        courier_service_dict = courier_dict['courier_service']
        courier_service = models.CourierService(
            courier_service_id=courier_service_dict['courier_service_id'],
            name=courier_service_dict['name'],
            address=courier_service_dict['address'],
            ogrn=courier_service_dict['ogrn'],
            work_schedule=courier_service_dict['work_schedule'],
            inn=courier_service_dict['tin'],
            vat=courier_service_dict['vat'],
            pg_db=pg_db['grocery_supply'],
        )
    return models.Courier(
        courier_id=courier_dict['courier_id'],
        courier_transport_type=courier_dict['courier_transport_type'],
        full_name=courier_dict['full_name'],
        courier_service=courier_service,
        phone_id=courier_dict['phone_id'],
        inn_id=courier_dict['tin_id'],
        billing_client_id=courier_dict['billing_client_id'],
        billing_type=courier_dict['billing_type'],
        eats_region_id=courier_dict.get('eats_region_id'),
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

COURIER_1 = {
    'courier_id': '1337',
    'full_name': 'Anton Antonov',
    'courier_transport_type': 'rover',
    'courier_service': COURIER_SERVICE,
    'phone_id': 'phone_id_1',
    'tin_id': 'tin_id_1',
    'billing_client_id': '123',
    'billing_type': 'courier_service',
    'eats_region_id': '194',
}


COURIER_2 = {
    'courier_id': '1234',
    'full_name': 'Anton Sidorov',
    'courier_transport_type': 'vehicle',
    'courier_service': None,
    'phone_id': 'phone_id_2',
    'tin_id': 'tin_id_2',
    'billing_client_id': '456',
    'billing_type': 'self_employed',
}


@pytest.mark.parametrize('courier', [COURIER_1, COURIER_2])
@pytest.mark.pgsql('grocery_supply')
async def test_basic(taxi_grocery_supply, pgsql, mockserver, courier):
    courier_model = make_courier(courier, pgsql)

    response = await taxi_grocery_supply.post(
        '/internal/v1/supply/v1/courier/info',
        json={'courier_id': courier_model.courier_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['courier_id'] == courier_model.courier_id
    assert body['full_name'] == courier_model.full_name
    assert body['transport_type'] == courier_model.courier_transport_type
    assert body['phone'] == courier_model.phone_id
    assert body['personal_phone_id'] == courier_model.phone_id
    assert body['personal_tin_id'] == courier_model.inn_id
    assert body['billing_client_id'] == courier_model.billing_client_id
    assert body['billing_type'] == courier_model.billing_type
    assert body.get('eats_region_id') == courier_model.eats_region_id
    if courier_model.courier_service:
        courier_service = body['courier_service']
        assert (
            courier_service['courier_service_id']
            == courier_model.courier_service.courier_service_id
        )
        assert courier_service['name'] == courier_model.courier_service.name
        assert (
            courier_service['address'] == courier_model.courier_service.address
        )
        assert courier_service['ogrn'] == courier_model.courier_service.ogrn
        assert (
            courier_service['work_schedule']
            == courier_model.courier_service.work_schedule
        )
        assert courier_service['tin'] == courier_model.courier_service.inn
        assert courier_service['vat'] == courier_model.courier_service.vat


async def test_courier_not_found(taxi_grocery_supply):
    response = await taxi_grocery_supply.post(
        '/internal/v1/supply/v1/courier/info', json={'courier_id': '1337'},
    )

    assert response.status_code == 404


@pytest.mark.pgsql('grocery_supply')
async def test_courier_no_tin(taxi_grocery_supply, pgsql, mockserver):
    courier = make_courier(COURIER_1, pgsql)
    courier.tin_id = None
    courier.save()

    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def mock_tins_personal(request):
        assert request.json['id'] == courier.tin_id
        return {'id': 'tin_id_1', 'value': 'tin'}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_phones_personal(request):
        assert request.json['id'] == courier.phone_id
        return {'id': 'phone_id_1', 'value': 'phone'}

    response = await taxi_grocery_supply.post(
        '/internal/v1/supply/v1/courier/info',
        json={'courier_id': courier.courier_id},
    )

    assert mock_tins_personal.times_called == 0

    assert response.status_code == 200
    assert 'tin' not in response.json()

import pytest

from tests_grocery_eats_gateway import headers


DEFAULT_COURIER_SERVICE = {
    'organization_name': 'Yandex',
    'legal_address': 'ул. Льва Толстого',
    'ogrn': '12345678910123',
    'work_schedule': 'performer_work_schedule',
}

DEFAULT_SELF_EMPLOYED = {
    'eats_courier_id': 'performer_courier_id',
    'courier_full_name': 'Ivan Ivanov Ivanovich',
    'tin': '1234567891012',
}


@pytest.mark.parametrize(
    'supply_info_response,expected_info',
    [
        pytest.param(
            {
                'organization_name': 'Yandex',
                'legal_address': 'ул. Льва Толстого',
                'ogrn': '12345678910123',
                'work_schedule': 'performer_work_schedule',
            },
            {
                'name': 'Yandex',
                'address': 'ул. Льва Толстого',
                'ogrn': '12345678910123',
                'workSchedule': 'performer_work_schedule',
                'type': 'courier_service',
                'summary': 'Yandex, ул. Льва Толстого, ОГРН 12345678910123',
            },
        ),
        pytest.param(
            {
                'eats_courier_id': 'performer_courier_id',
                'courier_full_name': 'Ivan Ivanov Ivanovich',
                'tin': '1234567891012',
            },
            {
                'firstName': 'Ivan',
                'lastName': 'Ivanov',
                'patronymic': 'Ivanovich',
                'inn': '7707083893',
                'type': 'self_employed',
                'summary': 'Ivan Ivanov Ivanovich, ИНН 7707083893',
            },
        ),
        pytest.param(
            {
                'eats_courier_id': 'performer_courier_id',
                'courier_full_name': 'Ivan Ivanov',
                'tin': '1234567891012',
            },
            {
                'firstName': 'Ivan',
                'lastName': 'Ivanov',
                'patronymic': '',
                'inn': '7707083893',
                'type': 'self_employed',
                'summary': 'Ivan Ivanov, ИНН 7707083893',
            },
        ),
    ],
)
async def test_basic(
        taxi_grocery_eats_gateway,
        grocery_orders,
        supply_info_response,
        expected_info,
):
    grocery_orders.set_supply_info_response(body=supply_info_response)

    response = await taxi_grocery_eats_gateway.get(
        '/delivery/v1/legal-info?order_id=order-id',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert grocery_orders.supply_info_times_called() == 1

    assert response.json()['payload']['legalInfo'] == expected_info


async def test_not_found(taxi_grocery_eats_gateway, grocery_orders):
    grocery_orders.set_supply_info_response(status_code=404)

    response = await taxi_grocery_eats_gateway.get(
        '/delivery/v1/legal-info?order_id=order-id',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 404
    assert grocery_orders.supply_info_times_called() == 1

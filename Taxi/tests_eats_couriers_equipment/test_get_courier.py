import pytest

GET_CORE_COURIER_HANDLER_PATH = (
    '/couriers-core/api/v1/general-information/couriers'
)

CORE_COURIER = {
    'courier': {
        'id': 123456,
        'first_name': 'Самозанят',
        'middle_name': 'Самозанятович',
        'last_name': 'Самозанятов',
        'phone_number': '6fda7ec82df145ec95de983070a3640c',
        'contact_email': '6182ad5e58e94dfbbf69009b8547eae3',
        'telegram_name': 'ae890f146d2e41bf8a044d770aa3f1dd',
        'billing_type': 'self_employed',
        'courier_type': 'pedestrian',
        'registration_country': {'name': 'Российская Федерация', 'code': 'RU'},
        'work_region': {'id': 1, 'name': 'Москва'},
        'project_type': None,
        'courier_service': None,
        'work_status': 'active',
        'work_status_updated_at': '2020-04-30T13:21:57+03:00',
        'source': None,
    },
}
EXPECTED_COURIER = {
    'data': {
        'attributes': {
            'createdAt': '2017-09-08T00:00:00+0000',
            'edaId': 123456,
            'emailPdId': '6182ad5e58e94dfbbf69009b8547eae3',
            'firstName': 'Самозанят',
            'lastName': 'Самозанятов',
            'middleName': 'Самозанятович',
            'phonePdId': '6fda7ec82df145ec95de983070a3640c',
            'telegramPdId': 'ae890f146d2e41bf8a044d770aa3f1dd',
            'uniformStatus': 'given',
            'updatedAt': '2017-09-08T00:00:00+0000',
            'vehicleStatus': 'given',
            'workStatusUpdatedAt': '2020-04-30T10:21:57+0000',
        },
        'id': 1,
        'relationships': {
            'workRegion': {'data': {'id': 1, 'type': 'region'}},
            'workStatus': {'data': {'id': 1, 'type': 'courier-work-status'}},
            'registrationCountry': {'data': {'id': 1, 'type': 'country'}},
            'billingType': {'data': {'id': 1, 'type': 'billing-type'}},
            'courierType': {'data': {'id': 1, 'type': 'courier-type'}},
        },
        'type': 'courier',
    },
    'included': [
        {'attributes': {'name': 'Москва'}, 'id': 1, 'type': 'region'},
        {
            'attributes': {'description': 'Активен', 'name': 'active'},
            'id': 1,
            'type': 'courier-work-status',
        },
        {
            'attributes': {'name': 'Российская Федерация'},
            'id': 1,
            'type': 'country',
        },
        {
            'attributes': {
                'name': 'self_employed',
                'description': 'Самозанят',
            },
            'id': 1,
            'type': 'billing-type',
        },
        {
            'attributes': {'name': 'pedestrian', 'description': 'Пешеход'},
            'id': 1,
            'type': 'courier-type',
        },
    ],
}

CORE_COURIER_FULL = {
    'courier': {
        'id': 123456,
        'first_name': 'First name',
        'middle_name': 'Patronymic',
        'last_name': 'Surname',
        'phone_number': '2f8c12f588b54cae8037e8c3180d3e4c',
        'contact_email': '9ef4a8ae52dc4f66adb4a5029e648c31',
        'telegram_name': 'fbe6e5ddf225455e8a300f0770256122',
        'billing_type': 'courier_service',
        'courier_type': 'pedestrian',
        'registration_country': {'name': 'Российская Федерация', 'code': 'RU'},
        'work_region': {'id': 1, 'name': 'Москва'},
        'project_type': 'eda',
        'courier_service': {'id': 146, 'name': 'Autotest courier service'},
        'work_status': 'deactivated',
        'work_status_updated_at': '2020-05-06T17:02:04+03:00',
        'source': 'selfregistration-form',
    },
}
EXPECTED_COURIER_FULL = {
    'data': {
        'attributes': {
            'createdAt': '2017-09-08T00:00:00+0000',
            'edaId': 123456,
            'emailPdId': '9ef4a8ae52dc4f66adb4a5029e648c31',
            'firstName': 'First name',
            'lastName': 'Surname',
            'middleName': 'Patronymic',
            'phonePdId': '2f8c12f588b54cae8037e8c3180d3e4c',
            'telegramPdId': 'fbe6e5ddf225455e8a300f0770256122',
            'uniformStatus': 'given',
            'updatedAt': '2017-09-08T00:00:00+0000',
            'vehicleStatus': 'given',
            'workStatusUpdatedAt': '2020-05-06T14:02:04+0000',
            'source': 'selfregistration-form',
        },
        'id': 1,
        'relationships': {
            'workRegion': {'data': {'id': 1, 'type': 'region'}},
            'workStatus': {'data': {'id': 3, 'type': 'courier-work-status'}},
            'registrationCountry': {'data': {'id': 1, 'type': 'country'}},
            'billingType': {'data': {'id': 2, 'type': 'billing-type'}},
            'courierType': {'data': {'id': 1, 'type': 'courier-type'}},
            'courierService': {'data': {'id': 1, 'type': 'courier-service'}},
            'projectType': {'data': {'id': 1, 'type': 'courier-project'}},
        },
        'type': 'courier',
    },
    'included': [
        {'attributes': {'name': 'Москва'}, 'id': 1, 'type': 'region'},
        {
            'attributes': {
                'description': 'Деактивирован',
                'name': 'deactivated',
            },
            'id': 3,
            'type': 'courier-work-status',
        },
        {
            'attributes': {'name': 'eda', 'description': 'Еда'},
            'id': 1,
            'type': 'courier-project',
        },
        {
            'attributes': {'name': 'Российская Федерация'},
            'id': 1,
            'type': 'country',
        },
        {
            'attributes': {'name': 'Autotest courier service'},
            'id': 1,
            'type': 'courier-service',
        },
        {
            'attributes': {
                'name': 'courier_service',
                'description': 'Курьерская служба',
            },
            'id': 2,
            'type': 'billing-type',
        },
        {
            'attributes': {'name': 'pedestrian', 'description': 'Пешеход'},
            'id': 1,
            'type': 'courier-type',
        },
    ],
}

SECOND_CORE_COURIER = {
    'courier': {
        'id': 123457,
        'first_name': 'Самозанят',
        'middle_name': 'Самозанятович',
        'last_name': 'Самозанятов',
        'phone_number': '6fda7ec82df145ec95de983070a3640c',
        'contact_email': '6182ad5e58e94dfbbf69009b8547eae3',
        'telegram_name': 'ae890f146d2e41bf8a044d770aa3f1dd',
        'billing_type': 'self_employed',
        'courier_type': 'pedestrian',
        'registration_country': {'name': 'Российская Федерация', 'code': 'RU'},
        'work_region': {'id': 1, 'name': 'Москва'},
        'project_type': 'eda',
        'courier_service': None,
        'work_status': 'active',
        'work_status_updated_at': '2020-04-30T13:21:57+03:00',
        'source': None,
    },
}
SECOND_EXPECTED_COURIER = {
    'data': {
        'attributes': {
            'createdAt': '2017-09-08T00:00:00+0000',
            'edaId': 123457,
            'emailPdId': '6182ad5e58e94dfbbf69009b8547eae3',
            'firstName': 'Самозанят',
            'lastName': 'Самозанятов',
            'middleName': 'Самозанятович',
            'phonePdId': '6fda7ec82df145ec95de983070a3640c',
            'telegramPdId': 'ae890f146d2e41bf8a044d770aa3f1dd',
            'uniformStatus': 'not-given',
            'updatedAt': '2017-09-08T00:00:00+0000',
            'vehicleStatus': 'given',
            'workStatusUpdatedAt': '2020-04-30T10:21:57+0000',
        },
        'id': 2,
        'relationships': {
            'workRegion': {'data': {'id': 1, 'type': 'region'}},
            'workStatus': {'data': {'id': 1, 'type': 'courier-work-status'}},
            'registrationCountry': {'data': {'id': 1, 'type': 'country'}},
            'billingType': {'data': {'id': 1, 'type': 'billing-type'}},
            'courierType': {'data': {'id': 1, 'type': 'courier-type'}},
            'projectType': {'data': {'id': 1, 'type': 'courier-project'}},
        },
        'type': 'courier',
    },
    'included': [
        {'attributes': {'name': 'Москва'}, 'id': 1, 'type': 'region'},
        {
            'attributes': {'description': 'Активен', 'name': 'active'},
            'id': 1,
            'type': 'courier-work-status',
        },
        {
            'attributes': {'name': 'eda', 'description': 'Еда'},
            'id': 1,
            'type': 'courier-project',
        },
        {
            'attributes': {'name': 'Российская Федерация'},
            'id': 1,
            'type': 'country',
        },
        {
            'attributes': {
                'name': 'self_employed',
                'description': 'Самозанят',
            },
            'id': 1,
            'type': 'billing-type',
        },
        {
            'attributes': {'name': 'pedestrian', 'description': 'Пешеход'},
            'id': 1,
            'type': 'courier-type',
        },
    ],
}
CORE_COURIER_WITH_NEW_BILLING_TYPE = {
    'courier': {
        'id': 123456,
        'first_name': 'Самозанят',
        'middle_name': 'Самозанятович',
        'last_name': 'Самозанятов',
        'phone_number': '6fda7ec82df145ec95de983070a3640c',
        'contact_email': '6182ad5e58e94dfbbf69009b8547eae3',
        'telegram_name': 'ae890f146d2e41bf8a044d770aa3f1dd',
        'billing_type': 'direct',
        'courier_type': 'pedestrian',
        'registration_country': {'name': 'Российская Федерация', 'code': 'RU'},
        'work_region': {'id': 1, 'name': 'Москва'},
        'project_type': None,
        'courier_service': None,
        'work_status': 'active',
        'work_status_updated_at': '2020-04-30T13:21:57+03:00',
        'source': None,
    },
}
EXPECTED_COURIER_WITH_NEW_BILLING_TYPE = {
    'data': {
        'attributes': {
            'createdAt': '2017-09-08T00:00:00+0000',
            'edaId': 123456,
            'emailPdId': '6182ad5e58e94dfbbf69009b8547eae3',
            'firstName': 'Самозанят',
            'lastName': 'Самозанятов',
            'middleName': 'Самозанятович',
            'phonePdId': '6fda7ec82df145ec95de983070a3640c',
            'telegramPdId': 'ae890f146d2e41bf8a044d770aa3f1dd',
            'uniformStatus': 'given',
            'updatedAt': '2017-09-08T00:00:00+0000',
            'vehicleStatus': 'given',
            'workStatusUpdatedAt': '2020-04-30T10:21:57+0000',
        },
        'id': 1,
        'relationships': {
            'workRegion': {'data': {'id': 1, 'type': 'region'}},
            'workStatus': {'data': {'id': 1, 'type': 'courier-work-status'}},
            'registrationCountry': {'data': {'id': 1, 'type': 'country'}},
            'billingType': {'data': {'id': 3, 'type': 'billing-type'}},
            'courierType': {'data': {'id': 1, 'type': 'courier-type'}},
        },
        'type': 'courier',
    },
    'included': [
        {'attributes': {'name': 'Москва'}, 'id': 1, 'type': 'region'},
        {
            'attributes': {'description': 'Активен', 'name': 'active'},
            'id': 1,
            'type': 'courier-work-status',
        },
        {
            'attributes': {'name': 'Российская Федерация'},
            'id': 1,
            'type': 'country',
        },
        {
            'attributes': {'name': 'direct', 'description': 'direct'},
            'id': 3,
            'type': 'billing-type',
        },
        {
            'attributes': {'name': 'pedestrian', 'description': 'Пешеход'},
            'id': 1,
            'type': 'courier-type',
        },
    ],
}


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier.sql',
        'add_uniform_types.sql',
        'add_places.sql',
        'add_users.sql',
        'link_couriers.sql',
    ],
)
@pytest.mark.parametrize(
    'eda_courier, expected_courier, courier_id',
    [
        (CORE_COURIER, EXPECTED_COURIER, 1),
        (CORE_COURIER_FULL, EXPECTED_COURIER_FULL, 1),
        (SECOND_CORE_COURIER, SECOND_EXPECTED_COURIER, 2),
        (
            CORE_COURIER_WITH_NEW_BILLING_TYPE,
            EXPECTED_COURIER_WITH_NEW_BILLING_TYPE,
            1,
        ),
    ],
)
async def test_get_courier(
        taxi_eats_couriers_equipment,
        mockserver,
        eda_courier,
        expected_courier,
        courier_id,
):
    @mockserver.json_handler(GET_CORE_COURIER_HANDLER_PATH, prefix=True)
    def _mock_courier_get(request):
        return eda_courier

    create_response = await taxi_eats_couriers_equipment.get(
        '/v1.0/couriers', params={'id': courier_id},
    )
    assert create_response.status_code == 200, create_response.text
    data = create_response.json()
    assert data == expected_courier
    assert _mock_courier_get.times_called == 1
    call = _mock_courier_get.next_call()
    assert dict(call['request'].query) == {'use_pd_ids': 'True'}
    assert (
        call['request'].path
        == f'{GET_CORE_COURIER_HANDLER_PATH}/{eda_courier["courier"]["id"]}'
    )


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=['add_courier_relations.sql', 'add_courier.sql'],
)
async def test_courier_not_found(taxi_eats_couriers_equipment):
    create_response = await taxi_eats_couriers_equipment.get(
        '/v1.0/couriers', params={'id': -1},
    )
    assert create_response.status_code == 404, create_response.text
    data = create_response.json()
    assert data == {
        'errors': [
            {
                'detail': 'Курьер с идентификатором -1 не найден',
                'source': {'pointer': 'id'},
                'title': 'Not found',
            },
        ],
    }


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=['add_courier_relations.sql', 'add_courier.sql'],
)
async def test_eda_courier_not_found(taxi_eats_couriers_equipment, mockserver):
    @mockserver.json_handler(GET_CORE_COURIER_HANDLER_PATH, prefix=True)
    def _mock_courier_get(request):
        return mockserver.make_response(json={}, status=404)

    create_response = await taxi_eats_couriers_equipment.get(
        '/v1.0/couriers', params={'id': 1},
    )
    assert create_response.status_code == 404, create_response.text
    data = create_response.json()
    assert data == {
        'errors': [
            {
                'detail': (
                    'Курьер с идентификатором 123456 не найден в сервисе еды'
                ),
                'source': {'pointer': 'id'},
                'title': 'Not found',
            },
        ],
    }
    assert _mock_courier_get.times_called == 1


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=['add_courier_relations.sql', 'add_courier.sql'],
)
@pytest.mark.parametrize('can_be_mocked', [True, False])
async def test_unexpected_relation(
        taxi_eats_couriers_equipment, mockserver, can_be_mocked,
):
    @mockserver.json_handler(GET_CORE_COURIER_HANDLER_PATH, prefix=True)
    def _mock_courier_get(request):
        courier = CORE_COURIER
        if can_be_mocked:
            courier['courier']['work_status'] = 'unexpected'
        return courier

    create_response = await taxi_eats_couriers_equipment.get(
        '/v1.0/couriers', params={'id': 1},
    )
    if can_be_mocked:
        assert create_response.status_code == 200, create_response.text
    assert _mock_courier_get.times_called == 1

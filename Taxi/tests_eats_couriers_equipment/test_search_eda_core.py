import pytest


CORE_COURIERS_HANDLER_PATH = (
    '/couriers-core/api/v1/general-information/couriers/catalog/search'
)

DEFAULT_PHONE = '79999999999'

COURIERS = [
    {
        'id': 592591,
        'first_name': 'Самозанят',
        'middle_name': 'Самозанятович',
        'last_name': 'Самозанятов',
        'phone_number': DEFAULT_PHONE,
        'contact_email': 'test@test.test',
        'billing_type': 'self_employed',
        'courier_type': 'pedestrian',
        'registration_country': {'name': 'Российская Федерация', 'code': 'RU'},
        'work_region': {'id': 1, 'name': 'Москва'},
        'project_type': 'eda',
        'courier_service': None,
        'work_status': 'active',
        'work_status_updated_at': '2018-04-30T13:21:57+03:00',
        'source': None,
    },
    {
        'id': 123456,
        'first_name': 'Курьер',
        'last_name': 'Курьеров',
        'phone_number': '78888888888',
        'telegram_name': 'samozanyat_courier',
        'billing_type': 'courier_service',
        'courier_type': 'pedestrian',
        'registration_country': {'name': 'Российская Федерация', 'code': 'RU'},
        'work_region': {'id': 2, 'name': 'Ярославль'},
        'project_type': None,
        'courier_service': {'id': 100, 'name': 'some-courier-service'},
        'work_status': 'active',
        'work_status_updated_at': '2018-04-30T13:21:57+03:00',
        'source': None,
        'comment': 'уточнить отчество',
    },
]

COURIERS_RESPONSE = {
    'data': [
        {
            'id': 592591,
            'type': 'courier',
            'attributes': {
                'phonePdId': '18d9c9ed14cf46538263a0a51f8a473a',
                'lastName': 'Самозанятов',
                'firstName': 'Самозанят',
                'middleName': 'Самозанятович',
                'workStatusUpdatedAt': '2018-04-30T10:21:57+0000',
            },
            'relationships': {
                'projectType': {'data': {'id': 1, 'type': 'courier-project'}},
                'workRegion': {'data': {'id': 1, 'type': 'region'}},
                'workStatus': {
                    'data': {'id': 1, 'type': 'courier-work-status'},
                },
                'billingType': {'data': {'id': 1, 'type': 'billing-type'}},
            },
        },
        {
            'id': 123456,
            'type': 'courier',
            'attributes': {
                'phonePdId': '28d9c9ed14cf46538263a0a51f8a473a',
                'courierId': 1,
                'lastName': 'Курьеров',
                'firstName': 'Курьер',
                'workStatusUpdatedAt': '2018-04-30T10:21:57+0000',
                'comment': 'уточнить отчество',
            },
            'relationships': {
                'workRegion': {'data': {'id': 2, 'type': 'region'}},
                'workStatus': {
                    'data': {'id': 1, 'type': 'courier-work-status'},
                },
                'billingType': {'data': {'id': 2, 'type': 'billing-type'}},
                'courierService': {
                    'data': {'id': 2, 'type': 'courier-service'},
                },
            },
        },
    ],
    'included': [
        {'attributes': {'name': 'Москва'}, 'id': 1, 'type': 'region'},
        {'attributes': {'name': 'Ярославль'}, 'id': 2, 'type': 'region'},
        {
            'attributes': {'name': 'active', 'description': 'Активен'},
            'id': 1,
            'type': 'courier-work-status',
        },
        {
            'attributes': {'name': 'eda', 'description': 'Еда'},
            'id': 1,
            'type': 'courier-project',
        },
        {
            'attributes': {'name': 'some-courier-service'},
            'id': 2,
            'type': 'courier-service',
        },
        {
            'attributes': {
                'description': 'Курьерская служба',
                'name': 'courier_service',
            },
            'id': 2,
            'type': 'billing-type',
        },
        {
            'attributes': {
                'description': 'Самозанят',
                'name': 'self_employed',
            },
            'id': 1,
            'type': 'billing-type',
        },
    ],
}

COURIERS_MOCK_RESPONSE = {
    'data': [
        {
            'id': 592591,
            'type': 'courier',
            'attributes': {
                'phonePdId': '18d9c9ed14cf46538263a0a51f8a473a',
                'lastName': 'Самозанятов',
                'firstName': 'Самозанят',
                'middleName': 'Самозанятович',
                'workStatusUpdatedAt': '2018-04-30T10:21:57+0000',
            },
            'relationships': {
                'projectType': {'data': {'id': 3, 'type': 'courier-project'}},
                'workRegion': {'data': {'id': 1, 'type': 'region'}},
                'workStatus': {
                    'data': {'id': 1, 'type': 'courier-work-status'},
                },
                'billingType': {'data': {'id': 1, 'type': 'billing-type'}},
            },
        },
    ],
    'included': [
        {'attributes': {'name': 'Москва'}, 'id': 1, 'type': 'region'},
        {
            'attributes': {'name': 'active', 'description': 'Активен'},
            'id': 1,
            'type': 'courier-work-status',
        },
        {
            'attributes': {'name': 'taxi', 'description': 'taxi'},
            'id': 3,
            'type': 'courier-project',
        },
        {
            'attributes': {
                'name': 'self_employed',
                'description': 'Самозанят',
            },
            'id': 1,
            'type': 'billing-type',
        },
    ],
}


def _make_request_params(phone, last_name, first_name, middle_name):
    params = {}
    if phone is not None:
        params['phone'] = phone
    if last_name is not None:
        params['lastName'] = last_name
    if first_name is not None:
        params['firstName'] = first_name
    if middle_name is not None:
        params['middleName'] = middle_name
    return params


@pytest.fixture(name='core_couriers_search_mock')
def _core_couriers_search_mock(mockserver):
    @mockserver.json_handler(CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_search(request):
        return {'couriers': COURIERS}

    return _mock_couriers_search


@pytest.mark.parametrize(
    'phone, last_name, first_name, middle_name',
    [
        (' +79999999999 ', None, None, None),
        (None, ' Курьеров', 'Курьер  ', None),
        ('79999999999', None, None, None),
        (None, '   Курьеров', 'Курьер', ' Курьерович'),
        ('79999999999', '   Курьеров', 'Курьер', ' Курьерович'),
    ],
)
@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=['add_courier_relations.sql', 'add_courier.sql'],
)
async def test_search_eda_core(
        taxi_eats_couriers_equipment,
        core_couriers_search_mock,
        personal_bulk_store,
        phone,
        last_name,
        first_name,
        middle_name,
):
    await _call_courier_eda(
        taxi_eats_couriers_equipment,
        core_couriers_search_mock,
        phone=phone,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        expected=COURIERS_RESPONSE,
        status=200,
        is_called_mock=True,
    )
    assert personal_bulk_store.times_called == 1
    call = await personal_bulk_store.wait_call()
    assert call['request'].json == {
        'items': [{'value': '+78888888888'}, {'value': '+79999999999'}],
        'validate': True,
    }


@pytest.mark.parametrize(
    'phone, last_name, first_name, middle_name, expected_error, is_called',
    [
        (
            ' +9999999       ',
            None,
            None,
            None,
            {
                'errors': [
                    {
                        'detail': 'Неправильный телефонный номер',
                        'source': {'pointer': 'phone'},
                        'title': 'Bad phone',
                    },
                ],
            },
            False,
        ),
        (
            None,
            None,
            None,
            None,
            {
                'errors': [
                    {
                        'detail': 'Значение не должно быть пустым',
                        'source': {'pointer': 'fullName'},
                        'title': 'Invalid Query Parameter',
                    },
                ],
            },
            False,
        ),
        (
            '+1234',
            'Курьеров',
            None,
            'Курьерович ',
            {
                'errors': [
                    {
                        'detail': 'Неправильный телефонный номер',
                        'source': {'pointer': 'phone'},
                        'title': 'Bad phone',
                    },
                    {
                        'detail': 'Значение не должно быть пустым',
                        'source': {'pointer': 'fullName'},
                        'title': 'Invalid Query Parameter',
                    },
                    {
                        'detail': 'Значение не должно быть пустым',
                        'source': {'pointer': 'firstName'},
                        'title': 'Invalid Query Parameter',
                    },
                ],
            },
            False,
        ),
        (
            f'+{DEFAULT_PHONE}',
            None,
            'Курьер',
            None,
            {
                'errors': [
                    {
                        'detail': 'Значение не должно быть пустым',
                        'source': {'pointer': 'fullName'},
                        'title': 'Invalid Query Parameter',
                    },
                    {
                        'detail': 'Значение не должно быть пустым',
                        'source': {'pointer': 'lastName'},
                        'title': 'Invalid Query Parameter',
                    },
                ],
            },
            False,
        ),
        (
            f'+{DEFAULT_PHONE}',
            'Курьеров',
            'Курьер',
            'Курьерович',
            {
                'errors': [
                    {
                        'detail': 'Значение не должно быть пустым.',
                        'title': 'Input format error',
                        'source': {'pointer': 'fullName.lastName'},
                    },
                ],
            },
            True,
        ),
    ],
)
async def test_validation_errors(
        taxi_eats_couriers_equipment,
        mockserver,
        phone,
        last_name,
        first_name,
        middle_name,
        expected_error,
        is_called,
):
    @mockserver.json_handler(CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_search(request):
        return mockserver.make_response(
            json={
                'domain': 'UserData',
                'code': 5,
                'err': 'Input format error',
                'errors': {
                    'fullName.lastName': ['Значение не должно быть пустым.'],
                },
            },
            status=400,
        )

    await _call_courier_eda(
        taxi_eats_couriers_equipment,
        _mock_couriers_search,
        phone=phone,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        expected=expected_error,
        status=422,
        is_called_mock=is_called,
    )


@pytest.mark.pgsql(
    'outsource-lavka-transport', files=['add_courier_relations.sql'],
)
async def test_wrong_type(
        taxi_eats_couriers_equipment, personal_bulk_store, mockserver,
):
    @mockserver.json_handler(CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_search(request):
        courier = COURIERS[0].copy()
        courier['project_type'] = 'taxi'
        return {'couriers': [courier]}

    await _call_courier_eda(
        taxi_eats_couriers_equipment,
        _mock_couriers_search,
        phone=DEFAULT_PHONE,
        expected=COURIERS_MOCK_RESPONSE,
        status=200,
        is_called_mock=True,
    )


@pytest.mark.pgsql(
    'outsource-lavka-transport', files=['add_courier_relations.sql'],
)
async def test_no_personal(
        taxi_eats_couriers_equipment,
        personal_empty_bulk_store,
        core_couriers_search_mock,
):
    expected_error = {
        'errors': [
            {
                'source': {'pointer': 'phone'},
                'detail': (
                    'Телефон +79999999999 не найден '
                    'в сервисе персональных данных'
                ),
                'title': 'Bad phone',
            },
        ],
    }
    await _call_courier_eda(
        taxi_eats_couriers_equipment,
        core_couriers_search_mock,
        phone=DEFAULT_PHONE,
        expected=expected_error,
        status=422,
        is_called_mock=True,
    )
    assert personal_empty_bulk_store.times_called == 1


@pytest.mark.pgsql(
    'outsource-lavka-transport', files=['add_courier_relations.sql'],
)
async def test_no_couriers(taxi_eats_couriers_equipment, mockserver):
    @mockserver.json_handler(CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_search(request):
        return {'couriers': []}

    expected = {'data': [], 'included': []}
    await _call_courier_eda(
        taxi_eats_couriers_equipment,
        _mock_couriers_search,
        phone=DEFAULT_PHONE,
        expected=expected,
        status=200,
        is_called_mock=True,
    )


async def _call_courier_eda(
        taxi_eats_couriers_equipment,
        mock,
        *,
        phone=None,
        last_name=None,
        first_name=None,
        middle_name=None,
        expected=None,
        status=200,
        is_called_mock=False,
):
    request_params = _make_request_params(
        phone, last_name, first_name, middle_name,
    )
    create_response = await taxi_eats_couriers_equipment.get(
        '/v1.0/couriers/eda', params=request_params,
    )
    assert create_response.status_code == status, create_response.text
    assert create_response.json() == expected
    if is_called_mock:
        assert mock.times_called == 1
        call = await mock.wait_call()
        params = {}
        if phone:
            params['phone'] = phone.strip()
        if last_name:
            params['last_name'] = last_name.strip()
        if first_name:
            params['first_name'] = first_name.strip()
        if middle_name:
            params['middle_name'] = middle_name.strip()
        assert dict(call['request'].query) == params
    else:
        assert not mock.times_called

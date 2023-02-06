import pytest


EXISTED_COURIER_ID = 123456
FIRST_POSSIBLE_ID = 3

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
        'comment': 'Это комментарий',
    },
}


def _build_courier_data(eda_id, use_project_type):
    data = {
        'data': {
            'type': 'courier',
            'attributes': {
                'edaId': eda_id,
                'firstName': 'Курьер',
                'lastName': 'Курьеров',
                'middleName': 'Курьерович',
                'phonePdId': '18d9c9ed14cf46538263a0a51f8a473a',
            },
            'relationships': {
                'workRegion': {'data': {'id': 1, 'type': 'region'}},
                'projectType': {'data': {'id': 1, 'type': 'courier-project'}},
                'workStatus': {'data': {'id': 1, 'type': 'courier-status'}},
                'billingType': {'data': {'id': 1, 'type': 'billing-type'}},
                'courierService': {
                    'data': {'id': 1, 'type': 'courier-service'},
                },
            },
        },
    }
    if use_project_type:
        data['data']['relationships'].update(
            {'projectType': {'data': {'id': 1, 'type': 'courier-project'}}},
        )
    return data


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=['add_courier_relations.sql', 'add_courier.sql'],
)
@pytest.mark.parametrize('use_project_type', [True, False])
async def test_create_courier(
        taxi_eats_couriers_equipment, mockserver, use_project_type, get_cursor,
):
    @mockserver.json_handler(GET_CORE_COURIER_HANDLER_PATH, prefix=True)
    def _mock_courier_get(request):
        return CORE_COURIER

    create_response = await _create_courier(
        taxi_eats_couriers_equipment,
        mockserver,
        use_project_type=use_project_type,
    )
    location = f'/v1.0/couriers?id={FIRST_POSSIBLE_ID}'
    assert create_response.status_code == 201, create_response.text
    assert create_response.json() == {}
    assert create_response.headers['Location'] == location

    cursor = get_cursor()
    cursor.execute(
        'SELECT id, courier_billing_type_id, courier_service_id, comment '
        'FROM couriers',
    )
    row = cursor.fetchall()[-1]
    assert row == [3, 1, 1, 'Это комментарий']


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=['add_courier_relations.sql', 'add_courier.sql'],
)
async def test_courier_conflict(taxi_eats_couriers_equipment, mockserver):
    create_response = await _create_courier(
        taxi_eats_couriers_equipment, mockserver, eda_id=EXISTED_COURIER_ID,
    )
    assert create_response.status_code == 409
    assert create_response.json() == {
        'errors': [
            {
                'detail': 'Курьер уже существует',
                'title': 'Unique violation',
                'source': {'pointer': 'edaId'},
            },
        ],
    }


async def _create_courier(
        taxi_eats_couriers_equipment,
        mockserver,
        *,
        eda_id=1,
        use_project_type=True,
):
    @mockserver.json_handler(GET_CORE_COURIER_HANDLER_PATH, prefix=True)
    def _mock_courier_get(request):
        return CORE_COURIER

    data = _build_courier_data(eda_id, use_project_type)
    create_response = await taxi_eats_couriers_equipment.post(
        '/v1.0/couriers', json=data,
    )
    return create_response

import pytest

TEST_EATS_ENROLLMENT_IN_HUB_HUBS_DATA = {
    'Московский Хаб 1': {
        'address': 'г. Москва, 1-я улица Строителей',
        'location_coordinates': {'lat': 39.60258, 'lon': 52.569089},
        'name': 'Хаб 1',
        'timezone': 'Europe/Moscow',
        'work_schedule': {
            '__default__': [
                {'from': '09:00', 'to': '13:00'},
                {'from': '14:00', 'to': '19:00'},
            ],
            'exclusions': [
                {
                    'date': '2022-01-03',
                    'schedule': [{'from': '11:00', 'to': '16:00'}],
                },
            ],
            'fri': [{'from': '09:00', 'to': '11:00'}],
            'sat': [{'from': '09:00', 'to': '12:00'}],
            'sun': [{'from': '10:00', 'to': '13:00'}],
        },
    },
}

HEADERS = {
    'Accept-Language': 'en',
    'Content-Type': 'application/json',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.60',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

BODY = {
    'date': '2022-02-30',
    'time_interval': {'from': '12:00', 'to': '13:00'},
}

HIRING_RESPONCE = {
    'code': 'SUCCESS',
    'message': 'Данные приняты.',
    'details': {'accepted_fields': ['Status', 'hub_address', 'hub date']},
}


@pytest.mark.config(
    EATS_ENROLLMENT_IN_HUB_HUBS_DATA=TEST_EATS_ENROLLMENT_IN_HUB_HUBS_DATA,
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    ['hub_id', 'courier_id', 'status_code'],
    [
        pytest.param('Московский Хаб 1', '111111', 200, id='Ok'),
        pytest.param('Московский Хаб 1', '555555', 400, id='No external_id'),
        pytest.param(
            'Не подходящий Хаб', '111111', 400, id='Wrong suitable hub',
        ),
    ],
)
async def test_register_in_hub(
        taxi_eats_enrollment_in_hub,
        mock_get_courier_profile,
        hub_id,
        courier_id,
        status_code,
):
    HEADERS['X-YaEda-CourierId'] = courier_id
    BODY['hub_identificator'] = hub_id

    response = await taxi_eats_enrollment_in_hub.post(
        '/driver/v1/enrollment-in-hub/v1/register-in-hub',
        headers=HEADERS,
        json=BODY,
    )

    assert response.status_code == status_code


@pytest.mark.now('2022-06-22T12:12:12.121212+0000')
@pytest.mark.translations()
@pytest.mark.parametrize(
    ['test_id'],
    [
        pytest.param('with_date_time'),
        pytest.param('with_date'),
        pytest.param('without_date_and_time'),
    ],
)
async def test_update_lead_stq(
        stq_runner,
        mockserver,
        mock_get_courier_profile,
        mock_driver_app_profile,
        test_id,
        load_json,
):
    data = load_json('hub_experiment.json')[test_id]

    @mockserver.json_handler('/hiring-api/v1/tickets/update')
    def _mock_hiring_api_update(request):
        assert request.json['fields'][2] == data['hiring-api-request']
        return mockserver.make_response(status=200, json=HIRING_RESPONCE)

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_general_sms_send(request):
        assert request.json == data['ucommunications-request']
        return {'message': '', 'code': '200'}

    await stq_runner.eats_enrollment_in_hub_update_lead.call(
        task_id='task id test', kwargs=data['kwargs'],
    )


@pytest.mark.config(
    EATS_ENROLLMENT_IN_HUB_HUBS_DATA=TEST_EATS_ENROLLMENT_IN_HUB_HUBS_DATA,
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_wrong_body(
        taxi_eats_enrollment_in_hub, mock_get_courier_profile,
):
    HEADERS['X-YaEda-CourierId'] = '111111'
    body = {
        'hub_identificator': 'Московский Хаб 1',
        'time_interval': {'from': '12:00', 'to': '13:00'},
    }

    response = await taxi_eats_enrollment_in_hub.post(
        '/driver/v1/enrollment-in-hub/v1/register-in-hub',
        headers=HEADERS,
        json=body,
    )

    assert response.json() == {
        'code': '400',
        'message': 'Time interval field can\'t be without date field',
    }
